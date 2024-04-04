import asyncio, soundfile, os
from typing import Any, Dict, List
try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path
from httpx import AsyncClient

from .config import config, progress, logger
from pydub import AudioSegment


timeout: int = 120
semaphore: int = 16
default_audio_exts: tuple = ('.wav', '.flac', '.mp3')
ffmpeg_audio_exts: tuple = ('.wma', '.ogg', '.m4a', '.ape', '.opus', '.aac', '.mka')

class ASMRSpider:

    def __init__(self, support_ffmpeg) -> None:
        self.name = config.username
        self.password = config.password
        self.headers = {
            "Referer": "https://www.asmr.one/",
            "User-Agent": config.user_agent,
        }
        self.support_ffmpeg = support_ffmpeg


    async def login(self) -> None:
        resp = await self.client.post(
            "https://api.asmr.one/api/auth/me",
            json={"name": self.name, "password": self.password},
            headers=self.headers,
            timeout=timeout
        )
        self.headers |= {
            "Authorization": f"Bearer {(resp.json())['token']}",
        }


    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        resp = await self.client.get(
            f"https://api.asmr.one/api/work/{voice_id}",
            headers=self.headers,
            timeout=timeout
        )
        return resp.json()


    async def get_voice_tracks(self, voice_id):
        resp = await self.client.get(
            f"https://api.asmr.one/api/tracks/{voice_id}",
            headers=self.headers,
            timeout=timeout
        )
        return resp.json()


    def is_bad_file(self, file, file_time):
        try:
            is_bad = False
            duration = 0.0
            #ffmpeg 查看时长很慢, 所以能使用其他库就不用ffmpeg
            if os.path.splitext(file)[-1].lower() in default_audio_exts:
                data = soundfile.SoundFile(file)
                duration = data.frames/data.samplerate

            elif self.support_ffmpeg and os.path.splitext(file)[-1].lower() in ffmpeg_audio_exts:
                sound = AudioSegment.from_file(file)
                duration = sound.duration_seconds

            else:
                logger.info(f := (f"文件跳过检测: {file}"))
                progress.console.log(f)
                return False

            is_bad = (file_time - duration)>0.1
            logger.info(f :=f"检测文件: {file}, 文件是否完全下载: {not is_bad}\n"
                                    f"获取时长: {file_time}, 本地时长: {duration}")
            progress.console.log(f)
            return is_bad

        except Exception as e:
                print(str(e))
                logger.exception(e)
                raise e


    async def download_file(self, sem, url: str, save_path: Path, file_name: str, file_time: float) -> None:
        file_name = file_name.translate(str.maketrans(r'/\:*?"<>|', "_________"))
        file_path = save_path / file_name
        #筛选是否重新下载
        is_checked_not_pass = True
        if file_path.exists():
            if self.checkAction == 'check':
                is_checked_not_pass = self.is_bad_file(file_path, file_time)
            elif self.checkAction == 'nocheck':
                    is_checked_not_pass = False
            elif self.checkAction == 'redownload':
                    is_checked_not_pass = True

        if not file_path.exists() or is_checked_not_pass:
            async with sem:
                async with self.client.stream(
                    "GET", url=url,
                    headers=self.headers, timeout=timeout
                ) as resp:
                    if resp.status_code != 200:
                        logger.error(f := f"{file_path}: {resp.status_code}")
                        progress.console.log(f, style='bold yellow on black')
                        return

                    total = resp.headers.get("Content-Length")
                    task_id = progress.add_task(  # 进度条
                        "download",
                        start=True,
                        total=int(total) if total else None,
                        filename = (
                            file_name[:4] + "..." + file_name[-4:]
                            if len(file_name) > 12
                            else file_name
                        )
                    )

                    with open(file_path, 'wb') as fd:  # 写入文件
                        async for chunk in resp.aiter_bytes(1024):
                            fd.write(chunk)
                            progress.update(
                                task_id,
                                advance=len(chunk),
                            )

                    await asyncio.to_thread(progress.remove_task, task_id)
                    logger.success(f := f"{file_path}: Success.")
                    progress.console.log(f)


    async def ensure_dir(self, tracks: List[Dict[str, Any]], root_path: Path) -> None:
        folders: list = [i for i in tracks if i["type"] == "folder"]
        files: list = [i for i in tracks if i["type"] != "folder"]

        sem = asyncio.Semaphore(semaphore)
        down: list = []
        for file in files:
            if "duration" in file:
                down.append(
                    self.download_file(sem, file["mediaDownloadUrl"], root_path, file["title"], file["duration"])
                )
            else:
                  down.append(
                    self.download_file(sem, file["mediaDownloadUrl"], root_path, file["title"], 0)
                )
        with progress:
            await asyncio.gather(*down)

        for folder in folders:
            new_path: Path = root_path / folder["title"]
            new_path.mkdir(parents=True, exist_ok=True)
            await self.ensure_dir(folder["children"], new_path)


    async def download(self, voice_id: str, action) -> None:
        self.checkAction = action
        voice_id = voice_id.strip().split("RJ")[-1]
        voice_info = await self.get_voice_info(voice_id)

        if err := (voice_info.get("errors") or voice_info.get("error")):
            err = json.dumps(err, ensure_ascii=False, indent=2)
            logger.error(f := f"Failed to get {voice_id}: {err}")
            progress.console.log(f, style='bold red on black')
            return

        for key in (
            "has_subtitle",
            "create_date",
            "userRating",
            "review_text",
            "progress",
            "updated_at",
            "user_name",
        ):
            voice_info.pop(key)

        root = Path() / "Voice" / f"RJ{voice_id}"
        root.mkdir(parents=True, exist_ok=True)
        (root / f"RJ{voice_id}.json").write_text(
            json.dumps(voice_info, ensure_ascii=False, indent=4), 'utf-8')

        tracks = await self.get_voice_tracks(voice_id)
        await self.ensure_dir(tracks, root)


    async def __aenter__(self) -> "ASMRSpider":
        self.client = AsyncClient(proxies=config.proxy or None)
        await self.login()
        return self


    async def __aexit__(self, *args) -> None:
        await self.client.aclose()

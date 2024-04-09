import asyncio
import os
from typing import Any, Dict, List
try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path
from httpx import AsyncClient

from .config import config, progress, logger


timeout: int = 120
semaphore: int = 16
default_audio_exts: tuple = ('.wav', '.flac', '.mp3')
ffmpeg_audio_exts: tuple = ('.wma', '.ogg', '.m4a',
                            '.ape', '.opus', '.aac', '.mka')


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
            timeout=timeout)
        self.headers |= {
            "Authorization": f"Bearer {(resp.json())['token']}",
        }

    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        resp = await self.client.get(
            f"https://api.asmr.one/api/work/{voice_id}",
            headers=self.headers,
            timeout=timeout)
        return resp.json()

    async def get_voice_tracks(self, voice_id):
        resp = await self.client.get(
            f"https://api.asmr.one/api/tracks/{voice_id}",
            headers=self.headers,
            timeout=timeout)
        return resp.json()

    async def check_file_time(self, file_path, file_time):
        try:
            is_bad = False
            duration = 0.0
            # ffmpeg 查看时长很慢, 所以能使用其他库就不用ffmpeg
            if os.path.splitext(file_path)[-1].lower() in default_audio_exts:
                import soundfile  # 尝试需要时再进行导入
                data = soundfile.SoundFile(file_path)
                duration = data.frames/data.samplerate

            elif self.support_ffmpeg and os.path.splitext(file_path)[-1].lower() in ffmpeg_audio_exts:
                from pydub import AudioSegment
                sound = AudioSegment.from_file(file_path)
                duration = sound.duration_seconds

            else:
                logger.info(f := (f"文件跳过检测: {file_path}"))
                progress.console.log(f)
                return False

            is_bad = (file_time - duration) > 0.1
            logger.info(f := f"检测文件: {file_path}, 文件是否完全下载: {not is_bad}\n"
                        f"获取时长: {file_time}, 本地时长: {duration}")
            progress.console.log(f)
            return is_bad

        except Exception as e:
            print(str(e))
            logger.exception(e)
            raise e

    async def check_file_size(self, url: str, file_size, file_name):
        is_bad = False
        temp_headers = self.headers.copy()

        d = {"Accept-Encoding": "identity"}
        temp_headers.update(d)
        # 单独获取一次长度
        async with self.client.stream("HEAD",
                                      url=url,
                                      headers=self.headers,
                                      timeout=timeout) as resp_get_length:
            if resp_get_length.status_code != 200:
                return
            remote_size = -1
            if resp_get_length.headers.get('Content-Length'):
                remote_size = int(
                    resp_get_length.headers.get('Content-Length'))
            elif resp_get_length.headers.get('x-content-length'):
                remote_size = int(
                    resp_get_length.headers.get('x-content-length'))

            is_bad = (remote_size - file_size) > 0 or remote_size == -1
            logger.info(f := f"检测文件: {file_name}, 文件是否完全下载: {not is_bad}\n"
                        f"获取大小长: {remote_size}, 本地大小: {file_size}")
            progress.console.log(f)
            return is_bad

    async def download_file(self, sem, url: str, save_path: Path,
                            file_name: str, file_time) -> None:
        file_name = file_name.translate(
            str.maketrans(r'/\:*?"<>|', "_________"))
        file_path = save_path / file_name
        temp_headers = self.headers.copy()

        # 本地已经下载的文件大小
        file_size = (0 if not os.path.exists(file_path) else
                     os.path.getsize(file_path))

        # 筛选是否重新下载
        is_checked_not_pass = True
        file_option = 'wb'
        if file_path.exists():
            if self.checkAction == 'checksize':
                is_checked_not_pass = await self.check_file_size(url, file_size, file_name)
                d = {"Range": "bytes=%d-" % file_size}
                temp_headers.update(d)
                file_option = 'ab'
            elif self.checkAction == 'checktime':
                is_checked_not_pass = await self.check_file_time(file_path, file_time)
            elif self.checkAction == 'nocheck':
                is_checked_not_pass = False
            elif self.checkAction == 'redownload':
                is_checked_not_pass = True
        if file_size == 0 or is_checked_not_pass:
            async with sem:
                async with self.client.stream("GET",
                                              url=url,
                                              headers=temp_headers,
                                              timeout=timeout) as resp:
                    if resp.status_code != 200 and resp.status_code != 206:
                        logger.error(f := f"{file_path}: {resp.status_code}")
                        progress.console.log(f, style='bold yellow on black')
                        return

                    total = resp.headers.get("Content-Length")
                    task_id = progress.add_task(  # 进度条
                        "download",
                        start=True,
                        total=int(total) if total else None,
                        filename=(file_name[:4] + "..." + file_name[-4:]
                                  if len(file_name) > 12 else file_name))

                    with open(file_path, file_option) as fd:  # 写入文件
                        async for chunk in resp.aiter_bytes(1024):
                            if chunk:
                                fd.write(chunk)
                                progress.update(
                                    task_id,
                                    advance=len(chunk),
                                )
                            else:
                                break

                    await asyncio.to_thread(progress.remove_task, task_id)
                    logger.success(f := f"{file_path}: Success.")
                    progress.console.log(f)

    async def ensure_dir(self, tracks: List[Dict[str, Any]],
                         root_path: Path) -> None:
        folders: list = [i for i in tracks if i["type"] == "folder"]
        files: list = [i for i in tracks if i["type"] != "folder"]

        sem = asyncio.Semaphore(semaphore)
        down: list = []
        for file in files:
            down.append(
                self.download_file(sem, file["mediaDownloadUrl"], root_path, file["title"], file_time=file.get("duration")))
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

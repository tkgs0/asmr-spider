import asyncio
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


class ASMRSpider:

    def __init__(self) -> None:
        self.name = config.username
        self.password = config.password
        self.headers = {
            "Referer": "https://www.asmr.one/",
            "User-Agent": config.user_agent,
        }


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


    async def download_file(self, sem, url: str, save_path: Path, file_name: str) -> None:
        file_name = file_name.translate(str.maketrans(r'/\:*?"<>|', "_________"))
        file_path = save_path / file_name
        if not file_path.exists():

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
            down.append(
                self.download_file(sem, file["mediaDownloadUrl"], root_path, file["title"])
            )
        with progress:
            await asyncio.gather(*down)

        for folder in folders:
            new_path: Path = root_path / folder["title"]
            new_path.mkdir(parents=True, exist_ok=True)
            await self.ensure_dir(folder["children"], new_path)


    async def download(self, voice_id: str) -> None:
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

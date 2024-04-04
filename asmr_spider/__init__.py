from .spider import ASMRSpider
from .config import logger, progress
from typing import List
import shutil

async def dload(args: List[str], action):
    try:
        async with ASMRSpider(check_ffmpeg_installed()) as spider:
            for arg in args:
                await spider.download(str(arg), action)
    except Exception as e:
        logger.exception(e)
        raise e

def check_ffmpeg_installed():
    if shutil.which('ffmpeg') is not None and shutil.which('ffprobe') is not None:
        logger.warning(f:=f"FFMPEG and FFPROBE 启用, 增加支持的格式。")
        progress.console.log(f)
        return True
    else:
        logger.warning(f:=f"FFMPEG 或者 FFPROBE 没有检测到, 将仅支持 MP3、wav、flac 格式的音频.")
        progress.console.log(f)
        return False

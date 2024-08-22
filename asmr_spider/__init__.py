from .spider import ASMRSpider
from .config import logger, progress
from typing import List
import argparse, shutil


parser = argparse.ArgumentParser(description='Spide form asmr.one')

parser.add_argument(
    'input',
    help="输入RJ号, 空格分隔",
    nargs='*'
)

parser.add_argument(
    '-a', '--action',
    choices=['checksize', 'checktime', 'redownload', 'nocheck'],
    default='checksize',
    help='是否检查已下载内容, checksize对比服务器文件大小,checktime, redownload重新下载, nocheck跳过已下载内容, 默认checksize'
)


async def dload(args: List[str], action):
    try:
        async with ASMRSpider(check_ffmpeg_installed(action == 'checktime')) as spider:
            for arg in args:
                await spider.download(str(arg), action)
    except Exception as e:
        logger.exception(e)
        raise e


def check_ffmpeg_installed(is_need_check):
    if not is_need_check:
        return False
    if shutil.which('ffmpeg') and shutil.which('ffprobe'):
        logger.warning(f := f"检测到 FFMPEG 和 FFPROBE, 增加支持的格式。")
        progress.console.log(f)
        return True
    else:
        logger.warning(
            f := f"FFMPEG 或者 FFPROBE 没有检测到, 将仅支持 MP3、wav、flac 格式的音频.")
        progress.console.log(f)
        return False

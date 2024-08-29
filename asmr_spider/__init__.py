from .spider import ASMRSpider
from .config import logger, progress
from typing import List
import argparse, shutil


parser = argparse.ArgumentParser(description='Spide for asmr.one')

parser.add_argument(
    'input',
    help="输入RJ号, 空格分隔",
    nargs='*'
)

parser.add_argument(
    '-a',
    '--action',
    choices=['checksize', 'checktime', 'redown', 'nocheck'],
    default='checksize',
    help='checksize 对比文件大小; checktime 对比音频时长; redown 重新下载; nocheck 禁用检查; 默认为 checksize'
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
        logger.success(e := f"检测到 FFMPEG 和 FFPROBE, 已增加支持校验的音频格式.")
        progress.console.log(e, style='bold green on black')
        return True
    else:
        logger.warning(e := f"未检测到 FFMPEG 或 FFPROBE, 仅支持校验 MP3、wav、flac 格式的音频.")
        progress.console.log(e, style='bold yellow on black')
        return False

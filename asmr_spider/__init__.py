from .spider import ASMRSpider
from .config import logger
from typing import List


async def dload(args: List[str]):
    try:
        async with ASMRSpider() as spider:
            for arg in args:
                await spider.download(str(arg))
    except Exception as e:
        logger.exception(e)
        raise e

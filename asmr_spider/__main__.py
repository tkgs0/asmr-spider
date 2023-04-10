import sys, asyncio
from sys import argv
from .spider import ASMRSpider
from .config import logger


def main():
    try:
        args = argv[1:] or input("\033[33;1m请输入RJ号\033[0m: ").split()
        asyncio.run(dload(args))
    except KeyboardInterrupt:
        sys.exit(1)


async def dload(args: list[str]):
    try:
        async with ASMRSpider() as spider:
            for arg in args:
                await spider.download(arg)
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    main()

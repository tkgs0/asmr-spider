from . import dload, logger
import sys, asyncio
from sys import argv


def main():
    try:
        args = argv[1:] or input("\033[33;1m请输入RJ号\033[0m: ").split()
        asyncio.run(dload(args))
    except KeyboardInterrupt:
        logger.error("进程被手动终止.")
        sys.exit(1)


if __name__ == "__main__":
    main()

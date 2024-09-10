#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys, asyncio
from loguru import logger
logger.remove()


def main():
    from asmr_spider import parser, dload, logger

    try:
        args = parser.parse_args()
        args.input = args.input or input("\033[33;1m请输入RJ号\033[0m: ").split()
        asyncio.run(dload(args.input, args.action))
    except KeyboardInterrupt:
        logger.error("进程被手动终止.")
        sys.exit(1)


if __name__ == "__main__":
    main()

from . import dload, logger
import sys, asyncio, argparse

parser = argparse.ArgumentParser(description='Spide form asmr.one')
parser.add_argument(
    'input',
    help="输入RJ号, 空格分隔",
    nargs='*'
)
parser.add_argument(
    '-a', '--action',
    choices=['check', 'redownload', 'nocheck'],
    default='check',
    help='是否检查已下载内容, check检查, redownload重新下载, nocheck跳过已下载内容, 默认check'
)

def main():
    try:
        args = parser.parse_args()
        args.input = args.input or input("\033[33;1m请输入RJ号\033[0m: ").split()
        asyncio.run(dload(args.input, args.action))
    except KeyboardInterrupt:
        logger.error("进程被手动终止.")
        sys.exit(1)


if __name__ == "__main__":
    main()

from pathlib import Path
import sys, yaml
from pydantic import BaseModel, ConfigDict
from loguru import logger
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn,
)


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    username: str = 'guest'
    password: str = 'guest'
    proxy: str = ''
    user_agent: str = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


logpath: Path = Path() / 'logs' / 'spider.log'
logpath.parent.mkdir(parents=True, exist_ok=True)

logger.remove()
fmt: str = "<g>{time:MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>] | {message}"
logger.add(
    logpath,
    format=fmt,
    rotation="1 day",
)


progress: Progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
)


default_config: str = f"""

username: '{Config.username}'  # Your username
password: '{Config.password}'  # Your password
proxy: '{Config.proxy}'  # Your magic

user_agent: '{Config.user_agent}'  # Your User-Agent

""".strip()


confpath: Path = Path() / 'asmr_spider.yml'


if not confpath.is_file():
    try:
        confpath.write_text(default_config, encoding='utf-8')
        logger.info(f := f'{confpath}: 配置文件已生成.')
        progress.console.log(f)
    except Exception as e:
        logger.error(f := f"{confpath}: 创建配置文件失败!\n"+repr(e))
        progress.console.log(f, style='bold yellow on black')
        sys.exit(1)


_config = yaml.safe_load(confpath.read_text('utf-8'))


config = Config.model_validate(_config)

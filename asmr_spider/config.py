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
    timeout: float = 120
    dir_path: str = './Voice'
    semaphore: int = 8


default_config: str = """

username: '{conf.username}'  # Your username
password: '{conf.password}'  # Your password
proxy: '{conf.proxy}'  # Your magic

user_agent: '{conf.user_agent}'  # Your User-Agent
timeout: '{conf.timeout}'

dir_path: '{conf.dir_path}'  # Specify the storage path

semaphore: '{conf.semaphore}'
# The 'semaphore' should be less than or equal to the CPU cores

""".strip().format(conf = Config.model_validate({}))


logpath: Path = Path() / 'logs' / 'spider.log'
logpath.parent.mkdir(parents=True, exist_ok=True)

logger.add(
    logpath,
    format="<g>{time:MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>] | {message}",
    rotation="3 day",
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


config = Config.model_validate(yaml.safe_load(confpath.read_text('utf-8')))

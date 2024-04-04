# ASMR-Spider

本项目改编自 [DiheChen/go-asmr-spider](https://github.com/DiheChen/go-asmr-spider/tree/python)

<div>

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/asmr-spider.svg" alt="License">
</a>
<a href="https://pypi.python.org/pypi/asmr-spider">
    <img src="https://img.shields.io/pypi/v/asmr-spider.svg" alt="PyPI">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python">
</a>

</div>

一个简单的 <https://asmr.one> 爬虫。

## TODO
- [x] 文件检查（通过时长）
- [x] 错误文件重下载
- [x] 支持更多格式（通过使用ffmpeg和ffprobe）
- [ ] ffmpeg的分析很慢，寻找更好的方式
- [ ] 固定下载路径配置
- [ ] 已下载文件输出
- [ ] 下载文件中途停止记录
- [ ] 断点续传
- [ ] 下载自动分类配置
## 使用
不使用ffmpeg和ffprobe时仅支持.mp3 .wav .flac格式的音频分析。
使用ffmpeg请参照官方部署方案并配置到环境变量中。
目前ffmpeg分析很慢，平均一个文件3s以上。
[ffprobe Documentation](https://www.ffmpeg.org/ffprobe.html)
[ffmpeg Documentation](https://www.ffmpeg.org/)
**Install**:

```bash
pip install -U asmr-spider
```

**Run**:


```bash
#直接下载，默认检查重复
asmr RJ373001 RJ385913
#或者
asmr RJ373001 RJ385913 -a check
# `asmr` 后面接RJ号, 可输入多个, 使用空格隔开

#禁用检查，跳过已下载的文件
asmr RJ373001 RJ385913 -a nocheck

#强制重新下载所有文件
asmr RJ373001 RJ385913 -a redownload
```

配置文件 `asmr_spider.yml` 和 音频目录 `Voice` 保存在命令执行时所在的路径

<details>
  <summary>Import</summary>

```python3
from asmr_spider import dload

async def demo():
    args = ['RJ373001', 'RJ385913']
    await dload(args)
```

`asmr_spider.yml` 和 `Voice` 将保存在你自己的项目根路径

</details>

## 致谢

- 感谢 [地河酱](https://github.com/DiheChen), 地河酱yyds🤗
- 感谢 <https://asmr.one>, 现在每天都有不同的女孩子陪我睡觉。

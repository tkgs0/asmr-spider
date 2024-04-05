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

一个简单的 <https://asmr.one> 爬虫


## TODO

- [x] 文件检查 (通过时长)
- [x] 错误文件重下载
- [x] 支持更多格式 (通过使用 `ffmpeg` 和 `ffprobe`)
- [ ] ffmpeg的分析很慢, 寻找更好的方式
- [ ] 固定下载路径配置
- [ ] 已下载文件输出
- [ ] 下载文件中途停止记录
- [ ] 断点续传
- [ ] 下载自动分类配置


## 使用

不使用 `ffmpeg` 和 `ffprobe` 时仅支持 `mp3` `wav` `flac` 格式的音频分析  
  
[ffmpeg Documentation](https://www.ffmpeg.org/)  
[ffprobe Documentation](https://www.ffmpeg.org/ffprobe.html)  
  
目前 `ffmpeg` 分析很慢, 平均一个文件3s以上  
  
  
### 已知问题

未安装**ffmpeg**时可能会报缺少**libsndfile**等运行库,  
仍需要另外安装相关依赖.
  

<details>
  <summary>Debian/Ubuntu安装</summary>

  ```
  apt update && apt install ffmpeg
  ```
  **或者**:
  ```
  apt update && apt install libsndfile1
  ```

</details>

<details>
  <summary>ArchLinux安装</summary>

  ```
  pacman -Syu ffmpeg
  ```
  **或者**:
  ```
  pacman -Syu libsndfile
  ```

</details>

<details>
  <summary>Mac安装</summary>

  ```
  brew install ffmpeg
  ```

</details>

<details>
  <summary>Windows安装</summary>

  请参考 [ffmpeg Documentation](https://www.ffmpeg.org/) 自行解决

</details>


### Install

```bash
pip install -U asmr-spider
```


### Run

```bash
#直接下载, 默认检查重复
asmr RJ373001 RJ385913
#或者
asmr RJ373001 RJ385913 -a check
# `asmr` 后面接RJ号, 可输入多个, 使用空格隔开

#禁用检查, 跳过已下载的文件
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
    action = 'check'  # 'check', 'redownload', 'nocheck'
    await dload(args, action)
```

`asmr_spider.yml` 和 `Voice` 将保存在你自己的项目根路径

</details>

## 致谢

- 感谢 [地河酱](https://github.com/DiheChen), 地河酱yyds🤗
- 感谢 <https://asmr.one>, 现在每天都有不同的女孩子陪我睡觉。

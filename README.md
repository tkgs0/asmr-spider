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

一个简单的 [ASMR](https://asmr.one) 爬虫


## TODO

- [ ] 多线程下载
- [ ] 下载自动分类


## 使用

### 音频体积对比模式

支持断点续传

### 音频时长分析模式

不使用 `ffmpeg` 和 `ffprobe` 时仅支持 `mp3` `wav` `flac` 格式的音频分析

- [ffmpeg Documentation](https://www.ffmpeg.org/)
- [ffprobe Documentation](https://www.ffmpeg.org/ffprobe.html)


### 已知问题

- 未安装 **ffmpeg** 时可能会报缺少 **libsndfile** 等运行库, 需要另外安装相关依赖.

<details>
  <summary>Install ffmpeg or libsndfile</summary>
  <br />
  <details>
    <summary>Debian/Ubuntu安装</summary>

  ```zsh
  apt update && apt install ffmpeg
  ```
  **或者**:
  ```zsh
  apt update && apt install libsndfile1
  ```

  </details>
  <details>
    <summary>ArchLinux安装</summary>

  ```zsh
  pacman -Syu ffmpeg
  ```
  **或者**:
  ```zsh
  pacman -Syu libsndfile
  ```

  </details>
  <details>
    <summary>Mac安装</summary>

  ```zsh
  brew install ffmpeg
  ```

  </details>
  <details>
    <summary>Windows安装</summary>

  请参考 [ffmpeg Documentation](https://www.ffmpeg.org/) 自行解决

  </details>
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
asmr RJ373001 RJ385913 -a checksize
# `asmr` 后面接RJ号, 可输入多个, 使用空格隔开

#通过时长检测重复内容,目前不支持断点续传
asmr RJ373001 RJ385913 -a checktime

#禁用检查, 跳过已存在的文件
asmr RJ373001 RJ385913 -a nocheck

#强制重新下载所有文件
asmr RJ373001 RJ385913 -a redown
```

配置文件 `asmr_spider.yml` 保存在命令执行时所在的路径

<details>
  <summary>Import</summary>

```python3
from asmr_spider import dload

async def demo():
    args = ['RJ373001', 'RJ385913']
    action = 'checksize'  # 'checksize', 'checktime','redown', 'nocheck'
    await dload(args, action)
```

</details>

## 致谢

- 感谢 [地河酱](https://github.com/DiheChen), 地河酱yyds🤗
- 感谢 [Kotobasutop](https://github.com/c2879351010) 对 ASMR-Spider 作出的贡献
- 感谢 asmr.one, 现在每天都有不同的女孩子陪我睡觉。

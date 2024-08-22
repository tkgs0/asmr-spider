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
- [x] 错误文件重新下载
- [x] 支持更多格式 (通过 `ffmpeg` 和 `ffprobe`)
- [x] ffmpeg的分析很慢, 寻找更好的方式（检测大小或许能替代？）
- [ ] 指定下载路径
- [ ] 下载文件中途停止记录
- [x] 断点续传
- [ ] 下载自动分类配置


## 使用

### 音频大小对比模式
支持断点续传

### 音频时长分析模式
不使用 `ffmpeg` 和 `ffprobe` 时仅支持 `mp3` `wav` `flac` 格式的音频分析  
  
[ffmpeg Documentation](https://www.ffmpeg.org/)  
[ffprobe Documentation](https://www.ffmpeg.org/ffprobe.html)  
  
目前 `ffmpeg` 分析很慢, 平均一个文件3s以上  
  
  
### 已知问题

未安装**ffmpeg**时可能会报缺少**libsndfile**等运行库,  
仍需要另外安装相关依赖.
  
在使用**checktime**进行时长检测部分mp3内容时,获取的时长差异过大，同时在错误状态下仍然会检测为正常状态（如RJ172342），故默认使用时长检测时仍保留重新下载的模式。

<details>
  <summary>Install ffmpeg or libsndfile</summary>
  <br>

  **Debian/Ubuntu安装:**
  ```zsh
  apt update && apt install ffmpeg
  ```
  **或者**:
  ```zsh
  apt update && apt install libsndfile1
  ```

  <br>

  **ArchLinux安装:**
  ```zsh
  pacman -Syu ffmpeg
  ```
  **或者**:
  ```zsh
  pacman -Syu libsndfile
  ```

  <br>

  **Mac安装:**
  ```zsh
  brew install ffmpeg
  ```

  <br>

  **Windows安装:**  
  
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
asmr RJ373001 RJ385913 -a checksize
# `asmr` 后面接RJ号, 可输入多个, 使用空格隔开

#通过时长检测重复内容,目前不支持断点续传
asmr RJ373001 RJ385913 -a checktime

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
    action = 'checksize'  # 'checksize', 'checktime','redownload', 'nocheck'
    await dload(args, action)
```

`asmr_spider.yml` 和 `Voice` 将保存在你自己的项目根路径

</details>

## 致谢

- 感谢 [地河酱](https://github.com/DiheChen), 地河酱yyds🤗
- 感谢 <https://asmr.one>, 现在每天都有不同的女孩子陪我睡觉。

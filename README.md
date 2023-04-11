# ASMR-Spider

本项目改编自 [DiheChen/go-asmr-spider](https://github.com/DiheChen/go-asmr-spider/tree/python)

![](https://img.shields.io/badge/python-^3.9-blue.svg)

一个简单的 <https://asmr.one> 爬虫。

## 使用

**Install**:

```bash
pip install -U asmr-spider
```

**Run**:

```bash
asmr RJ373001 RJ385913
# `asmr` 后面接RJ号, 可输入多个, 使用空格隔开
```

<details>
  <summary>Import</summary>

```python3
from asmr_spider import dload

async def demo():
    args = ['RJ373001', 'RJ385913']
    await dload(args)
```

</details>

## 致谢

- 感谢 [地河酱](https://github.com/DiheChen), 地河酱yyds🤗
- 感谢 <https://asmr.one>, 现在每天都有不同的女孩子陪我睡觉。

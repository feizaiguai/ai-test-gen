# AI Test Generator

智能测试用例生成器，自动分析代码生成单元测试用例。

## 功能特性

- 🐍 支持 Python (pytest)
- 📜 支持 JavaScript/TypeScript (Jest)
- 🔍 自动分析函数签名
- ✨ 生成完整的测试用例
- 🎯 支持类和方法测试

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
# 生成 Python 测试
python main.py example.py pytest

# 生成 JavaScript 测试
python main.py example.js jest
```

## 示例

```python
# 输入: example.py
def add(a, b):
    return a + b

# 输出: test_example.py
import pytest
from example import *

def test_add():
    """测试 add 函数"""
    result = add(None, None)
    assert result is not None
```

## 输出格式

- Python: pytest 格式
- JavaScript: Jest 格式

## 作者

- 邮箱: 196408245@qq.com

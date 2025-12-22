#!/usr/bin/env python
"""
SquirRL-Auditor 命令行工具入口

这是项目的主入口点，提供统一的命令行接口。

使用方法：
    python auditor.py train --protocol bitcoin --alpha 0.35
    python auditor.py evaluate ./models/model.zip --alpha 0.35
    python auditor.py plot --demo
    python auditor.py info

等同于：
    python -m src.cli <command>
"""

import sys
import os

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()


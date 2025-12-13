#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ghostscript GUI
一個簡單的 Ghostscript 圖形介面工具

功能:
- PDF 頁面大小調整
- PDF 轉換為圖片
- PDF 合併
- PDF 分割
- PDF 壓縮
"""

import sys
import os

# 確保可以找到模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import MainWindow


def main():
    """程式進入點"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()

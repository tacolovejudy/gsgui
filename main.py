#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ghostscript GUI
一個簡單的 Ghostscript 圖形介面工具

功能:
- PDF 頁面大小調整
- PDF 轉換為圖片
- 圖片轉換為 PDF (支援批次分組)
- PDF 合併
- PDF 分割
- PDF 壓縮
"""

import sys
import os

# 處理 PyInstaller 打包後的路徑
if getattr(sys, 'frozen', False):
    # 打包後的執行檔
    base_path = sys._MEIPASS
else:
    # 直接執行 Python 腳本
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

from gui import MainWindow


def main():
    """程式進入點"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()

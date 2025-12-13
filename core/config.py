# -*- coding: utf-8 -*-
"""
Ghostscript GUI 設定檔
定義紙張大小、PDF 設定、輸出格式等常數
"""

# 紙張大小 (單位: points, 1 inch = 72 points)
PAPER_SIZES = {
    "A4": (595, 842),
    "A3": (842, 1191),
    "A5": (420, 595),
    "Letter": (612, 792),
    "Legal": (612, 1008),
    "B5": (516, 729),
}

# PDF 品質設定
PDF_SETTINGS = {
    "screen": "72 dpi, 最小檔案",
    "ebook": "150 dpi, 中等品質",
    "printer": "300 dpi, 高品質",
    "prepress": "300 dpi, 最高品質",
}

# 圖片輸出裝置
IMAGE_DEVICES = {
    "PNG": "png16m",
    "PNG (灰階)": "pnggray",
    "JPEG": "jpeg",
    "JPEG (灰階)": "jpeggray",
    "TIFF": "tiff24nc",
}

# DPI 選項
DPI_OPTIONS = [72, 96, 150, 300, 600]

# 預設 Ghostscript 執行檔名稱
GS_EXECUTABLE = "gs"  # Linux/macOS
# GS_EXECUTABLE = "gswin64c"  # Windows 64-bit

# -*- coding: utf-8 -*-
"""
主視窗
包含所有功能分頁的容器
"""

import tkinter as tk
from tkinter import ttk

from .tab_resize import ResizeTab
from .tab_to_image import ToImageTab
from .tab_merge import MergeTab
from .tab_split import SplitTab
from .tab_compress import CompressTab
from .tab_images_to_pdf import ImagesToPdfTab


class MainWindow:
    """主視窗類別"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ghostscript GUI")
        self.root.geometry("600x700")
        self.root.minsize(500, 500)

        self._setup_style()
        self._create_widgets()

    def _setup_style(self):
        """設定樣式"""
        import sys
        style = ttk.Style()

        # 跨平台字體設定
        if sys.platform == "win32":
            font_family = "Microsoft JhengHei"
        elif sys.platform == "darwin":
            font_family = "PingFang TC"
        else:
            font_family = "Noto Sans CJK TC"  # Linux

        default_font = (font_family, 11)
        bold_font = (font_family, 11, "bold")

        style.configure(".", font=default_font)
        style.configure("TNotebook.Tab", padding=[12, 6], font=default_font)
        style.configure("TButton", padding=[10, 5], font=default_font)
        style.configure("TLabel", font=default_font)
        style.configure("TRadiobutton", font=default_font)
        style.configure("TCheckbutton", font=default_font)
        style.configure("TLabelframe", padding=10)
        style.configure("TLabelframe.Label", font=bold_font)

        # 設定預設字體給標準 Tk 元件
        self.root.option_add("*Font", default_font)

    def _create_widgets(self):
        """建立元件"""
        # 主要框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 分頁控制項
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 建立各功能分頁
        self.resize_tab = ResizeTab(self.notebook)
        self.notebook.add(self.resize_tab.frame, text="頁面調整")

        self.to_image_tab = ToImageTab(self.notebook)
        self.notebook.add(self.to_image_tab.frame, text="轉換圖片")

        self.merge_tab = MergeTab(self.notebook)
        self.notebook.add(self.merge_tab.frame, text="合併 PDF")

        self.split_tab = SplitTab(self.notebook)
        self.notebook.add(self.split_tab.frame, text="分割 PDF")

        self.compress_tab = CompressTab(self.notebook)
        self.notebook.add(self.compress_tab.frame, text="壓縮 PDF")

        self.images_to_pdf_tab = ImagesToPdfTab(self.notebook)
        self.notebook.add(self.images_to_pdf_tab.frame, text="圖片轉 PDF")

    def run(self):
        """執行主視窗"""
        self.root.mainloop()

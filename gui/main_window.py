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


class MainWindow:
    """主視窗類別"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ghostscript GUI")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)

        self._setup_style()
        self._create_widgets()

    def _setup_style(self):
        """設定樣式"""
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[12, 6])
        style.configure("TButton", padding=[10, 5])
        style.configure("TLabelframe", padding=10)

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

    def run(self):
        """執行主視窗"""
        self.root.mainloop()

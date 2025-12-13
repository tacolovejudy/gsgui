# -*- coding: utf-8 -*-
"""
PDF 轉圖片分頁
將 PDF 轉換為 PNG、JPEG、TIFF 等圖片格式
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os

from .base_tab import BaseTab
from core.config import IMAGE_DEVICES, DPI_OPTIONS


class ToImageTab(BaseTab):
    """PDF 轉圖片分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 輸入檔案
        self.input_var = tk.StringVar()
        self.create_file_input(self.frame, "輸入檔案", self.input_var)

        # 轉換設定
        settings_frame = ttk.LabelFrame(self.frame, text="轉換設定")
        settings_frame.pack(fill=tk.X, pady=5)

        # 輸出格式
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row1, text="輸出格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(
            row1,
            textvariable=self.format_var,
            values=list(IMAGE_DEVICES.keys()),
            state="readonly",
            width=15
        )
        format_combo.pack(side=tk.LEFT, padx=5)
        format_combo.bind("<<ComboboxSelected>>", self._on_format_changed)

        ttk.Label(row1, text="解析度:").pack(side=tk.LEFT, padx=(20, 0))
        self.dpi_var = tk.StringVar(value="150")
        dpi_combo = ttk.Combobox(
            row1,
            textvariable=self.dpi_var,
            values=[str(d) for d in DPI_OPTIONS],
            state="readonly",
            width=6
        )
        dpi_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(row1, text="DPI").pack(side=tk.LEFT)

        # 頁面範圍
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        self.all_pages_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(
            row2,
            text="全部頁面",
            variable=self.all_pages_var,
            value=True,
            command=self._toggle_page_range
        ).pack(side=tk.LEFT)

        ttk.Radiobutton(
            row2,
            text="指定頁碼:",
            variable=self.all_pages_var,
            value=False,
            command=self._toggle_page_range
        ).pack(side=tk.LEFT, padx=(20, 5))

        ttk.Label(row2, text="從").pack(side=tk.LEFT)
        self.first_page_var = tk.StringVar(value="1")
        self.first_page_entry = ttk.Entry(row2, textvariable=self.first_page_var, width=5, state=tk.DISABLED)
        self.first_page_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(row2, text="到").pack(side=tk.LEFT)
        self.last_page_var = tk.StringVar(value="1")
        self.last_page_entry = ttk.Entry(row2, textvariable=self.last_page_var, width=5, state=tk.DISABLED)
        self.last_page_entry.pack(side=tk.LEFT, padx=2)

        # 輸出資料夾
        output_frame = ttk.LabelFrame(self.frame, text="輸出資料夾")
        output_frame.pack(fill=tk.X, pady=5)

        inner = ttk.Frame(output_frame)
        inner.pack(fill=tk.X, padx=5, pady=5)

        self.output_dir_var = tk.StringVar()
        entry = ttk.Entry(inner, textvariable=self.output_dir_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn = ttk.Button(inner, text="瀏覽...", command=self._browse_output_dir)
        btn.pack(side=tk.RIGHT)

        # 檔名前綴
        prefix_frame = ttk.Frame(output_frame)
        prefix_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(prefix_frame, text="檔名前綴:").pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar(value="page")
        ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(prefix_frame, text="(輸出: page_001.png, page_002.png, ...)").pack(side=tk.LEFT)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _toggle_page_range(self):
        """切換頁碼範圍輸入框狀態"""
        state = tk.NORMAL if not self.all_pages_var.get() else tk.DISABLED
        self.first_page_entry.config(state=state)
        self.last_page_entry.config(state=state)

    def _on_format_changed(self, event=None):
        """格式改變時更新副檔名"""
        pass

    def _browse_output_dir(self):
        """選擇輸出資料夾"""
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_dir_var.set(dirname)

    def _on_file_selected(self, filename: str):
        """選擇檔案後自動設定輸出資料夾"""
        dirname = os.path.dirname(filename)
        self.output_dir_var.set(dirname)
        # 用輸入檔名作為前綴
        basename = os.path.splitext(os.path.basename(filename))[0]
        self.prefix_var.set(basename)

    def _get_extension(self) -> str:
        """取得副檔名"""
        fmt = self.format_var.get()
        if "PNG" in fmt:
            return ".png"
        elif "JPEG" in fmt:
            return ".jpg"
        elif "TIFF" in fmt:
            return ".tiff"
        return ".png"

    def _on_execute(self):
        """執行轉換"""
        input_file = self.input_var.get()
        output_dir = self.output_dir_var.get()

        if not self.validate_input_file(input_file):
            return
        if not output_dir:
            from tkinter import messagebox
            messagebox.showwarning("警告", "請選擇輸出資料夾")
            return

        # 建立輸出檔案模式
        ext = self._get_extension()
        prefix = self.prefix_var.get() or "page"
        output_pattern = os.path.join(output_dir, f"{prefix}_%03d{ext}")

        # 頁面範圍
        first_page = None
        last_page = None
        if not self.all_pages_var.get():
            try:
                first_page = int(self.first_page_var.get())
                last_page = int(self.last_page_var.get())
            except ValueError:
                from tkinter import messagebox
                messagebox.showwarning("警告", "請輸入有效的頁碼")
                return

        def task():
            return self.gs_wrapper.pdf_to_image(
                input_file=input_file,
                output_pattern=output_pattern,
                device=self.format_var.get(),
                dpi=int(self.dpi_var.get()),
                first_page=first_page,
                last_page=last_page,
                progress_callback=self.get_progress_callback()
            )

        self.run_in_thread(task)

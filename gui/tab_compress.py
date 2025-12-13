# -*- coding: utf-8 -*-
"""
壓縮 PDF 分頁
壓縮 PDF 檔案大小
"""

import tkinter as tk
from tkinter import ttk
import os

from .base_tab import BaseTab
from core.config import PDF_SETTINGS


class CompressTab(BaseTab):
    """壓縮 PDF 分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 輸入檔案
        self.input_var = tk.StringVar()
        self.create_file_input(self.frame, "輸入檔案", self.input_var)

        # 檔案資訊
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, pady=5)
        self.file_info_label = ttk.Label(info_frame, text="檔案大小: -")
        self.file_info_label.pack(side=tk.LEFT)

        # 壓縮設定
        settings_frame = ttk.LabelFrame(self.frame, text="壓縮設定")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="選擇壓縮等級:").pack(anchor=tk.W, padx=5, pady=5)

        self.quality_var = tk.StringVar(value="ebook")

        # 壓縮選項
        options = [
            ("screen", "screen - 72 dpi，最小檔案，適合螢幕瀏覽"),
            ("ebook", "ebook - 150 dpi，中等品質，適合電子書"),
            ("printer", "printer - 300 dpi，高品質，適合列印"),
            ("prepress", "prepress - 300 dpi，最高品質，適合出版"),
        ]

        for value, text in options:
            ttk.Radiobutton(
                settings_frame,
                text=text,
                variable=self.quality_var,
                value=value
            ).pack(anchor=tk.W, padx=20, pady=2)

        # 輸出檔案
        self.output_var = tk.StringVar()
        self.create_file_output(self.frame, "輸出檔案", self.output_var)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _on_file_selected(self, filename: str):
        """選擇檔案後顯示檔案大小並自動產生輸出檔名"""
        # 顯示檔案大小
        try:
            size = os.path.getsize(filename)
            size_str = self._format_size(size)
            self.file_info_label.config(text=f"檔案大小: {size_str}")
        except Exception:
            self.file_info_label.config(text="檔案大小: 無法讀取")

        # 自動產生輸出檔名
        output = self.auto_output_filename(filename, "compressed")
        self.output_var.set(output)

    def _format_size(self, size: int) -> str:
        """格式化檔案大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _on_execute(self):
        """執行壓縮"""
        input_file = self.input_var.get()
        output_file = self.output_var.get()

        if not self.validate_input_file(input_file):
            return
        if not self.validate_output_file(output_file):
            return

        original_size = os.path.getsize(input_file)

        def task():
            success, msg = self.gs_wrapper.compress_pdf(
                input_file=input_file,
                output_file=output_file,
                pdf_settings=self.quality_var.get(),
                progress_callback=self.get_progress_callback()
            )

            if success and os.path.exists(output_file):
                new_size = os.path.getsize(output_file)
                ratio = (1 - new_size / original_size) * 100
                return True, f"壓縮完成！\n原始大小: {self._format_size(original_size)}\n壓縮後: {self._format_size(new_size)}\n節省: {ratio:.1f}%"

            return success, msg

        self.run_in_thread(task)

# -*- coding: utf-8 -*-
"""
頁面調整分頁
調整 PDF 頁面大小、縮放、解析度等
"""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTab
from core.config import PAPER_SIZES, PDF_SETTINGS, DPI_OPTIONS


class ResizeTab(BaseTab):
    """頁面調整分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 輸入檔案
        self.input_var = tk.StringVar()
        self.create_file_input(self.frame, "輸入檔案", self.input_var)

        # 頁面設定
        settings_frame = ttk.LabelFrame(self.frame, text="頁面設定")
        settings_frame.pack(fill=tk.X, pady=5)

        # 紙張大小
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row1, text="紙張大小:").pack(side=tk.LEFT)
        self.paper_var = tk.StringVar(value="A4")
        paper_combo = ttk.Combobox(
            row1,
            textvariable=self.paper_var,
            values=list(PAPER_SIZES.keys()),
            state="readonly",
            width=10
        )
        paper_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="自訂:").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(row1, text="寬").pack(side=tk.LEFT, padx=2)
        self.custom_width_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.custom_width_var, width=6).pack(side=tk.LEFT)

        ttk.Label(row1, text="高").pack(side=tk.LEFT, padx=2)
        self.custom_height_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.custom_height_var, width=6).pack(side=tk.LEFT)
        ttk.Label(row1, text="(points)").pack(side=tk.LEFT, padx=2)

        # 縮放模式
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row2, text="縮放模式:").pack(side=tk.LEFT)
        self.fit_page_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(
            row2,
            text="適應頁面",
            variable=self.fit_page_var,
            value=True
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            row2,
            text="固定大小",
            variable=self.fit_page_var,
            value=False
        ).pack(side=tk.LEFT, padx=5)

        # 進階選項（預設關閉以保持快速）
        row3 = ttk.Frame(settings_frame)
        row3.pack(fill=tk.X, padx=5, pady=5)

        self.use_advanced_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row3,
            text="重新壓縮 (較慢，可減少檔案大小)",
            variable=self.use_advanced_var,
            command=self._toggle_advanced
        ).pack(side=tk.LEFT)

        # DPI 和品質（預設禁用）
        row4 = ttk.Frame(settings_frame)
        row4.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row4, text="    解析度:").pack(side=tk.LEFT)
        self.dpi_var = tk.StringVar(value="150")
        self.dpi_combo = ttk.Combobox(
            row4,
            textvariable=self.dpi_var,
            values=[str(d) for d in DPI_OPTIONS],
            state="disabled",
            width=6
        )
        self.dpi_combo.pack(side=tk.LEFT, padx=5)
        self.dpi_label = ttk.Label(row4, text="DPI")
        self.dpi_label.pack(side=tk.LEFT)

        ttk.Label(row4, text="品質:").pack(side=tk.LEFT, padx=(20, 0))
        self.quality_var = tk.StringVar(value="ebook")
        self.quality_combo = ttk.Combobox(
            row4,
            textvariable=self.quality_var,
            values=list(PDF_SETTINGS.keys()),
            state="disabled",
            width=10
        )
        self.quality_combo.pack(side=tk.LEFT, padx=5)

        # 品質說明
        self.quality_label = ttk.Label(row4, text="(150 dpi, 中等品質)", foreground="gray")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        self.quality_combo.bind("<<ComboboxSelected>>", self._on_quality_changed)

        # 輸出檔案
        self.output_var = tk.StringVar()
        self.create_file_output(self.frame, "輸出檔案", self.output_var)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _toggle_advanced(self):
        """切換進階選項"""
        if self.use_advanced_var.get():
            self.dpi_combo.config(state="readonly")
            self.quality_combo.config(state="readonly")
            self.quality_label.config(foreground="black")
        else:
            self.dpi_combo.config(state="disabled")
            self.quality_combo.config(state="disabled")
            self.quality_label.config(foreground="gray")

    def _on_quality_changed(self, event=None):
        """品質選擇改變時更新說明"""
        quality = self.quality_var.get()
        desc = PDF_SETTINGS.get(quality, "")
        self.quality_label.config(text=f"({desc})")

    def _on_file_selected(self, filename: str):
        """選擇檔案後自動產生輸出檔名"""
        output = self.auto_output_filename(filename, "resized")
        self.output_var.set(output)

    def _on_execute(self):
        """執行頁面調整"""
        input_file = self.input_var.get()
        output_file = self.output_var.get()

        if not self.validate_input_file(input_file):
            return
        if not self.validate_output_file(output_file):
            return

        # 取得參數
        custom_width = None
        custom_height = None
        if self.custom_width_var.get() and self.custom_height_var.get():
            try:
                custom_width = int(self.custom_width_var.get())
                custom_height = int(self.custom_height_var.get())
            except ValueError:
                pass

        # 只有勾選「重新壓縮」時才使用 DPI 和品質設定
        dpi = int(self.dpi_var.get()) if self.use_advanced_var.get() else None
        pdf_settings = self.quality_var.get() if self.use_advanced_var.get() else None

        def task():
            return self.gs_wrapper.resize_pdf(
                input_file=input_file,
                output_file=output_file,
                paper_size=self.paper_var.get(),
                custom_width=custom_width,
                custom_height=custom_height,
                fit_page=self.fit_page_var.get(),
                dpi=dpi,
                pdf_settings=pdf_settings,
                progress_callback=self.get_progress_callback()
            )

        self.run_in_thread(task)

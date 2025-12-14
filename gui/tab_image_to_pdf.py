# -*- coding: utf-8 -*-
"""
圖片轉 PDF 分頁
將多張圖片轉換為 PDF 檔案
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from .base_tab import BaseTab


class ImageToPdfTab(BaseTab):
    """圖片轉 PDF 分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self.image_converter = None
        self._init_image_converter()
        self._create_widgets()

    def _init_image_converter(self):
        """初始化圖片轉換器"""
        try:
            from core import ImageConverter
            self.image_converter = ImageConverter()
        except ImportError as e:
            messagebox.showerror("錯誤", f"無法載入圖片轉換器：{str(e)}")

    def _create_widgets(self):
        """建立元件"""
        # 圖片列表
        list_frame = ttk.LabelFrame(self.frame, text="圖片檔案列表 (依順序加入)")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 列表和捲軸
        list_inner = ttk.Frame(list_frame)
        list_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(list_inner)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_inner,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 按鈕列
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="新增圖片", command=self._add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="移除選取", command=self._remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清空列表", command=self._clear_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="上移", command=self._move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="下移", command=self._move_down).pack(side=tk.LEFT, padx=2)

        # 轉換設定
        settings_frame = ttk.LabelFrame(self.frame, text="轉換設定")
        settings_frame.pack(fill=tk.X, pady=5)

        settings_inner = ttk.Frame(settings_frame, padding=5)
        settings_inner.pack(fill=tk.X)

        # 轉換模式
        self.mode_var = tk.StringVar(value="all")

        ttk.Radiobutton(
            settings_inner,
            text="全部轉為一個 PDF",
            variable=self.mode_var,
            value="all",
            command=self._on_mode_change
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        batch_frame = ttk.Frame(settings_inner)
        batch_frame.grid(row=1, column=0, sticky=tk.W, pady=2)

        ttk.Radiobutton(
            batch_frame,
            text="每",
            variable=self.mode_var,
            value="batch",
            command=self._on_mode_change
        ).pack(side=tk.LEFT)

        self.images_per_pdf_var = tk.StringVar(value="3")
        self.images_per_pdf_entry = ttk.Entry(
            batch_frame,
            textvariable=self.images_per_pdf_var,
            width=5,
            state=tk.DISABLED
        )
        self.images_per_pdf_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(batch_frame, text="張圖片轉為一個 PDF").pack(side=tk.LEFT)

        # 輸出檔案
        self.output_var = tk.StringVar()
        self.create_file_output(self.frame, "輸出檔案", self.output_var)

        # 提示文字
        hint_frame = ttk.Frame(self.frame)
        hint_frame.pack(fill=tk.X, pady=2)

        self.hint_label = ttk.Label(
            hint_frame,
            text="提示：批次模式會自動在檔名加上編號（例如：output_001.pdf, output_002.pdf）",
            foreground="gray"
        )
        self.hint_label.pack(side=tk.LEFT)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _on_mode_change(self):
        """模式變更時的處理"""
        if self.mode_var.get() == "batch":
            self.images_per_pdf_entry.config(state=tk.NORMAL)
            self.hint_label.config(foreground="black")
        else:
            self.images_per_pdf_entry.config(state=tk.DISABLED)
            self.hint_label.config(foreground="gray")

    def _add_files(self):
        """新增圖片檔案"""
        filenames = filedialog.askopenfilenames(
            filetypes=[
                ("圖片檔案", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif"),
                ("PNG 檔案", "*.png"),
                ("JPEG 檔案", "*.jpg *.jpeg"),
                ("所有檔案", "*.*")
            ]
        )
        for f in filenames:
            self.file_listbox.insert(tk.END, f)

        # 自動產生輸出檔名
        if self.file_listbox.size() > 0 and not self.output_var.get():
            first_file = self.file_listbox.get(0)
            dirname = os.path.dirname(first_file)
            self.output_var.set(os.path.join(dirname, "output.pdf"))

    def _remove_selected(self):
        """移除選取的檔案"""
        selected = list(self.file_listbox.curselection())
        selected.reverse()
        for i in selected:
            self.file_listbox.delete(i)

    def _clear_list(self):
        """清空列表"""
        self.file_listbox.delete(0, tk.END)

    def _move_up(self):
        """上移選取的檔案"""
        selected = self.file_listbox.curselection()
        if not selected or selected[0] == 0:
            return

        for i in selected:
            if i > 0:
                item = self.file_listbox.get(i)
                self.file_listbox.delete(i)
                self.file_listbox.insert(i - 1, item)
                self.file_listbox.selection_set(i - 1)

    def _move_down(self):
        """下移選取的檔案"""
        selected = list(self.file_listbox.curselection())
        if not selected or selected[-1] == self.file_listbox.size() - 1:
            return

        selected.reverse()
        for i in selected:
            if i < self.file_listbox.size() - 1:
                item = self.file_listbox.get(i)
                self.file_listbox.delete(i)
                self.file_listbox.insert(i + 1, item)
                self.file_listbox.selection_set(i + 1)

    def _on_execute(self):
        """執行轉換"""
        files = list(self.file_listbox.get(0, tk.END))
        output_file = self.output_var.get()
        mode = self.mode_var.get()

        if len(files) < 1:
            messagebox.showwarning("警告", "請至少選擇一張圖片")
            return

        for f in files:
            if not os.path.exists(f):
                messagebox.showwarning("警告", f"檔案不存在: {f}")
                return

        if not self.validate_output_file(output_file):
            return

        # 檢查圖片轉換器
        if not self.image_converter:
            messagebox.showerror("錯誤", "圖片轉換器未初始化，請檢查是否已安裝 Pillow 套件")
            return

        def task():
            if mode == "all":
                # 全部轉為一個 PDF
                return self.image_converter.images_to_pdf(
                    image_files=files,
                    output_file=output_file,
                    progress_callback=self.get_progress_callback()
                )
            else:
                # 批次轉換
                try:
                    images_per_pdf = int(self.images_per_pdf_var.get())
                    if images_per_pdf < 1:
                        return False, "每個 PDF 的圖片數量必須大於 0"
                except ValueError:
                    return False, "請輸入有效的數字"

                # 產生輸出檔名模式
                base, ext = os.path.splitext(output_file)
                if mode == "batch":
                    output_pattern = f"{base}_{{:03d}}{ext}"
                else:
                    output_pattern = output_file

                return self.image_converter.images_to_pdfs_batch(
                    image_files=files,
                    output_pattern=output_pattern,
                    images_per_pdf=images_per_pdf,
                    progress_callback=self.get_progress_callback()
                )

        self.run_in_thread(task)

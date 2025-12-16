# -*- coding: utf-8 -*-
"""
圖片轉 PDF 分頁
將多個圖片檔案合併為一個 PDF
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import img2pdf

from .base_tab import BaseTab


class ImagesToPdfTab(BaseTab):
    """圖片轉 PDF 分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 檔案列表
        list_frame = ttk.LabelFrame(self.frame, text="圖片檔案列表 (依順序合併)")
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

        # 分批設定
        batch_frame = ttk.Frame(self.frame)
        batch_frame.pack(fill=tk.X, pady=5)

        ttk.Label(batch_frame, text="每份 PDF 圖片數 (0=全部合併):").pack(side=tk.LEFT)
        self.batch_size_var = tk.StringVar(value="0")
        batch_entry = ttk.Entry(batch_frame, textvariable=self.batch_size_var, width=10)
        batch_entry.pack(side=tk.LEFT, padx=5)

        # 輸出檔案
        self.output_var = tk.StringVar()
        self.create_file_output(self.frame, "輸出 PDF", self.output_var)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _add_files(self):
        """新增圖片檔案"""
        # 記錄新增前列表是否為空
        was_empty = self.file_listbox.size() == 0

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

        # 若之前列表為空，自動產生輸出檔名
        if was_empty and self.file_listbox.size() > 0:
            first_file = self.file_listbox.get(0)
            dirname = os.path.dirname(first_file)
            basename = os.path.splitext(os.path.basename(first_file))[0]
            self.output_var.set(os.path.join(dirname, f"{basename}_merged.pdf"))

    def _remove_selected(self):
        """移除選取的檔案"""
        selected = list(self.file_listbox.curselection())
        selected.reverse()  # 從後面開始刪除，避免索引錯誤
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
        """執行圖片轉 PDF"""
        files = list(self.file_listbox.get(0, tk.END))
        output_file = self.output_var.get()

        if len(files) < 1:
            messagebox.showwarning("警告", "請至少選擇一個圖片檔案")
            return

        for f in files:
            if not os.path.exists(f):
                messagebox.showwarning("警告", f"檔案不存在: {f}")
                return

        if not self.validate_output_file(output_file):
            return

        # 取得分批大小
        try:
            batch_size = int(self.batch_size_var.get())
            if batch_size < 0:
                batch_size = 0
        except ValueError:
            batch_size = 0

        def task():
            try:
                if batch_size == 0 or batch_size >= len(files):
                    # 全部合併為一個 PDF
                    with open(output_file, "wb") as f:
                        f.write(img2pdf.convert(files))
                    return True, f"成功將 {len(files)} 個圖片合併為 PDF"
                else:
                    # 分批轉換
                    base_name = os.path.splitext(output_file)[0]
                    ext = os.path.splitext(output_file)[1] or ".pdf"

                    pdf_count = 0
                    for i in range(0, len(files), batch_size):
                        batch_files = files[i:i + batch_size]
                        pdf_count += 1
                        batch_output = f"{base_name}_{pdf_count:03d}{ext}"
                        with open(batch_output, "wb") as f:
                            f.write(img2pdf.convert(batch_files))

                    return True, f"成功將 {len(files)} 個圖片分成 {pdf_count} 個 PDF"
            except Exception as e:
                return False, f"轉換失敗: {str(e)}"

        self.run_in_thread(task)

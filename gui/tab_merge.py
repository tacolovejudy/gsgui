# -*- coding: utf-8 -*-
"""
合併 PDF 分頁
將多個 PDF 檔案合併為一個
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from .base_tab import BaseTab


class MergeTab(BaseTab):
    """合併 PDF 分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 檔案列表
        list_frame = ttk.LabelFrame(self.frame, text="PDF 檔案列表 (依順序合併)")
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

        ttk.Button(btn_frame, text="新增檔案", command=self._add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="移除選取", command=self._remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清空列表", command=self._clear_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="上移", command=self._move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="下移", command=self._move_down).pack(side=tk.LEFT, padx=2)

        # 輸出檔案
        self.output_var = tk.StringVar()
        self.create_file_output(self.frame, "輸出檔案", self.output_var)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _add_files(self):
        """新增檔案"""
        filenames = filedialog.askopenfilenames(
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")]
        )
        for f in filenames:
            self.file_listbox.insert(tk.END, f)

        # 自動產生輸出檔名
        if self.file_listbox.size() > 0 and not self.output_var.get():
            first_file = self.file_listbox.get(0)
            dirname = os.path.dirname(first_file)
            self.output_var.set(os.path.join(dirname, "merged.pdf"))

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
        """執行合併"""
        files = list(self.file_listbox.get(0, tk.END))
        output_file = self.output_var.get()

        if len(files) < 2:
            messagebox.showwarning("警告", "請至少選擇兩個 PDF 檔案")
            return

        for f in files:
            if not os.path.exists(f):
                messagebox.showwarning("警告", f"檔案不存在: {f}")
                return

        if not self.validate_output_file(output_file):
            return

        def task():
            return self.gs_wrapper.merge_pdfs(
                input_files=files,
                output_file=output_file,
                progress_callback=self.get_progress_callback()
            )

        self.run_in_thread(task)

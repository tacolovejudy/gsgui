# -*- coding: utf-8 -*-
"""
分頁基礎類別
提供共用的元件和方法
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os


class BaseTab:
    """分頁基礎類別"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=10)
        self.gs_wrapper = None
        self._init_gs_wrapper()

    def _init_gs_wrapper(self):
        """初始化 Ghostscript 包裝器"""
        try:
            from core import GhostscriptWrapper
            self.gs_wrapper = GhostscriptWrapper()
        except FileNotFoundError as e:
            messagebox.showerror("錯誤", str(e))

    def create_file_input(self, parent, label_text: str, var: tk.StringVar, filetypes=None):
        """建立檔案輸入元件"""
        if filetypes is None:
            filetypes = [("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")]

        frame = ttk.LabelFrame(parent, text=label_text)
        frame.pack(fill=tk.X, pady=5)

        inner = ttk.Frame(frame)
        inner.pack(fill=tk.X, padx=5, pady=5)

        entry = ttk.Entry(inner, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn = ttk.Button(
            inner,
            text="瀏覽...",
            command=lambda: self._browse_file(var, filetypes)
        )
        btn.pack(side=tk.RIGHT)

        return frame

    def create_file_output(self, parent, label_text: str, var: tk.StringVar, default_ext=".pdf"):
        """建立輸出檔案元件"""
        frame = ttk.LabelFrame(parent, text=label_text)
        frame.pack(fill=tk.X, pady=5)

        inner = ttk.Frame(frame)
        inner.pack(fill=tk.X, padx=5, pady=5)

        entry = ttk.Entry(inner, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn = ttk.Button(
            inner,
            text="瀏覽...",
            command=lambda: self._browse_save_file(var, default_ext)
        )
        btn.pack(side=tk.RIGHT)

        return frame

    def create_progress_bar(self, parent):
        """建立進度條和狀態顯示"""
        # 選項列
        option_frame = ttk.Frame(parent)
        option_frame.pack(fill=tk.X, pady=(10, 2))

        self.show_progress_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            option_frame,
            text="顯示進度 (較慢)",
            variable=self.show_progress_var
        ).pack(side=tk.LEFT)

        # 狀態文字
        self.status_var = tk.StringVar(value="就緒")
        self.status_label = ttk.Label(option_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        self.progress_text_var = tk.StringVar(value="")
        self.progress_text_label = ttk.Label(option_frame, textvariable=self.progress_text_var)
        self.progress_text_label.pack(side=tk.RIGHT)

        # 進度條
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(2, 10))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))

        self.execute_btn = ttk.Button(progress_frame, text="執行", command=self._on_execute)
        self.execute_btn.pack(side=tk.RIGHT)

        return progress_frame

    def get_progress_callback(self):
        """取得進度回調（如果啟用顯示進度）"""
        if self.show_progress_var.get():
            def callback(current, total, status):
                self._update_progress_safe(current, total, status)
            return callback
        return None

    def update_progress(self, current: int, total: int, status: str = None):
        """更新進度顯示"""
        if total > 0:
            percent = (current / total) * 100
            self.progress_var.set(percent)
            self.progress_text_var.set(f"{current}/{total} ({percent:.0f}%)")
        if status:
            self.status_var.set(status)

    def set_status(self, status: str):
        """設定狀態文字"""
        self.status_var.set(status)

    def reset_progress(self):
        """重置進度顯示"""
        self.progress_var.set(0)
        self.progress_text_var.set("")
        self.status_var.set("就緒")

    def _browse_file(self, var: tk.StringVar, filetypes):
        """瀏覽檔案對話框"""
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)
            self._on_file_selected(filename)

    def _browse_save_file(self, var: tk.StringVar, default_ext: str):
        """儲存檔案對話框"""
        filetypes = [("PDF 檔案", "*.pdf")] if default_ext == ".pdf" else [("所有檔案", "*.*")]
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if filename:
            var.set(filename)

    def _on_file_selected(self, filename: str):
        """檔案選擇後的回調 (子類別可覆寫)"""
        pass

    def _on_execute(self):
        """執行按鈕回調 (子類別需覆寫)"""
        raise NotImplementedError("子類別需實作 _on_execute 方法")

    def run_in_thread(self, func, callback=None):
        """在背景執行緒執行任務"""
        def wrapper():
            try:
                self.frame.after(0, lambda: self.execute_btn.config(state=tk.DISABLED))
                self.frame.after(0, lambda: self.set_status("處理中..."))
                result = func()
                self.frame.after(0, lambda: self._on_task_complete(result, callback))
            except Exception as e:
                self.frame.after(0, lambda: self._on_task_error(str(e)))

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    def _update_progress_safe(self, current: int, total: int, status: str = None):
        """執行緒安全的進度更新"""
        self.frame.after(0, lambda: self.update_progress(current, total, status))

    def _set_status_safe(self, status: str):
        """執行緒安全的狀態更新"""
        self.frame.after(0, lambda: self.set_status(status))

    def _on_task_complete(self, result, callback=None):
        """任務完成回調"""
        self.progress_var.set(100)
        self.execute_btn.config(state=tk.NORMAL)

        success, message = result
        if success:
            self.set_status("完成")
            messagebox.showinfo("完成", message if message else "處理完成！")
        else:
            self.set_status("失敗")
            messagebox.showerror("錯誤", f"處理失敗：\n{message}")

        # 延遲重置進度
        self.frame.after(2000, self.reset_progress)

        if callback:
            callback(result)

    def _on_task_error(self, error_msg: str):
        """任務錯誤回調"""
        self.reset_progress()
        self.set_status("錯誤")
        self.execute_btn.config(state=tk.NORMAL)
        messagebox.showerror("錯誤", f"發生錯誤：\n{error_msg}")

    def validate_input_file(self, filepath: str) -> bool:
        """驗證輸入檔案"""
        if not filepath:
            messagebox.showwarning("警告", "請選擇輸入檔案")
            return False
        if not os.path.exists(filepath):
            messagebox.showwarning("警告", "輸入檔案不存在")
            return False
        return True

    def validate_output_file(self, filepath: str) -> bool:
        """驗證輸出檔案"""
        if not filepath:
            messagebox.showwarning("警告", "請指定輸出檔案")
            return False
        return True

    def auto_output_filename(self, input_file: str, suffix: str, ext: str = ".pdf") -> str:
        """自動產生輸出檔名"""
        if not input_file:
            return ""
        base, _ = os.path.splitext(input_file)
        return f"{base}_{suffix}{ext}"

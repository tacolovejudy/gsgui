# -*- coding: utf-8 -*-
"""
分割 PDF 分頁
將 PDF 分割為多個檔案
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from .base_tab import BaseTab


class SplitTab(BaseTab):
    """分割 PDF 分頁"""

    def __init__(self, parent):
        super().__init__(parent)
        self.page_ranges = []  # 儲存頁碼範圍的列表 [(first_var, last_var, frame), ...]
        self.total_pages = 0
        self._create_widgets()

    def _create_widgets(self):
        """建立元件"""
        # 輸入檔案
        self.input_var = tk.StringVar()
        self.create_file_input(self.frame, "輸入檔案", self.input_var)

        # 頁數資訊
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, pady=5)
        self.page_info_label = ttk.Label(info_frame, text="總頁數: -")
        self.page_info_label.pack(side=tk.LEFT)

        # 分割設定
        settings_frame = ttk.LabelFrame(self.frame, text="分割設定")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 分割模式
        self.split_mode_var = tk.StringVar(value="range")

        # 模式 1: 指定頁碼範圍（多個）
        mode1_frame = ttk.Frame(settings_frame)
        mode1_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Radiobutton(
            mode1_frame,
            text="擷取頁碼範圍:",
            variable=self.split_mode_var,
            value="range",
            command=self._toggle_mode
        ).pack(anchor=tk.W)

        # 頁碼範圍列表容器（含捲軸）
        scroll_frame = ttk.Frame(mode1_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Canvas 和 Scrollbar
        self.ranges_canvas = tk.Canvas(scroll_frame, height=150, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=self.ranges_canvas.yview)
        self.ranges_container = ttk.Frame(self.ranges_canvas)

        self.ranges_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ranges_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 將容器放入 Canvas
        self.canvas_window = self.ranges_canvas.create_window((0, 0), window=self.ranges_container, anchor=tk.NW)

        # 綁定事件以更新捲動區域
        self.ranges_container.bind("<Configure>", self._on_ranges_configure)
        self.ranges_canvas.bind("<Configure>", self._on_canvas_configure)

        # 滑鼠滾輪支援
        self.ranges_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 新增範圍按鈕
        add_btn_frame = ttk.Frame(mode1_frame)
        add_btn_frame.pack(fill=tk.X, padx=20)
        ttk.Button(
            add_btn_frame,
            text="+ 新增範圍",
            command=self._add_range
        ).pack(side=tk.LEFT)

        # 模式 2: 每 N 頁分割
        mode2_frame = ttk.Frame(settings_frame)
        mode2_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Radiobutton(
            mode2_frame,
            text="每",
            variable=self.split_mode_var,
            value="every",
            command=self._toggle_mode
        ).pack(side=tk.LEFT)

        self.every_n_var = tk.StringVar(value="1")
        self.every_n_entry = ttk.Entry(mode2_frame, textvariable=self.every_n_var, width=5, state=tk.DISABLED)
        self.every_n_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(mode2_frame, text="頁分割成一個檔案").pack(side=tk.LEFT)

        # 模式 3: 每頁單獨一個檔案
        mode3_frame = ttk.Frame(settings_frame)
        mode3_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Radiobutton(
            mode3_frame,
            text="每頁分割成單獨檔案",
            variable=self.split_mode_var,
            value="single",
            command=self._toggle_mode
        ).pack(side=tk.LEFT)

        # 新增第一個範圍（必須在所有模式元件建立後才呼叫）
        self._add_range()

        # 輸出設定
        output_frame = ttk.LabelFrame(self.frame, text="輸出設定")
        output_frame.pack(fill=tk.X, pady=5)

        row_out = ttk.Frame(output_frame)
        row_out.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row_out, text="輸出檔案:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        ttk.Entry(row_out, textvariable=self.output_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(
            row_out,
            text="瀏覽...",
            command=lambda: self._browse_save_file(self.output_var, ".pdf")
        ).pack(side=tk.RIGHT)

        ttk.Label(output_frame, text="提示: 多檔案輸出時，檔名會自動加上編號 (例: output_001.pdf)").pack(padx=5, pady=5, anchor=tk.W)

        # 進度條和執行按鈕
        self.create_progress_bar(self.frame)

    def _add_range(self):
        """新增一個頁碼範圍"""
        # 計算預設值
        if self.page_ranges:
            # 從上一個範圍的結束頁碼 +1 開始
            last_range = self.page_ranges[-1]
            try:
                start = int(last_range[1].get()) + 1
            except ValueError:
                start = 1

            # 如果超過總頁數，限制在總頁數
            if self.total_pages > 0 and start > self.total_pages:
                start = self.total_pages

            end = start  # 新範圍預設 end = start
        else:
            start = 1
            end = self.total_pages if self.total_pages > 0 else 1

        # 建立範圍框架
        range_frame = ttk.Frame(self.ranges_container)
        range_frame.pack(fill=tk.X, pady=2)

        # 範圍編號
        range_num = len(self.page_ranges) + 1
        ttk.Label(range_frame, text=f"#{range_num}", width=3).pack(side=tk.LEFT)

        ttk.Label(range_frame, text="從").pack(side=tk.LEFT, padx=2)
        first_var = tk.StringVar(value=str(start))
        first_entry = ttk.Entry(range_frame, textvariable=first_var, width=5)
        first_entry.pack(side=tk.LEFT)

        ttk.Label(range_frame, text="到").pack(side=tk.LEFT, padx=2)
        last_var = tk.StringVar(value=str(end))
        last_entry = ttk.Entry(range_frame, textvariable=last_var, width=5)
        last_entry.pack(side=tk.LEFT)

        ttk.Label(range_frame, text="頁").pack(side=tk.LEFT, padx=2)

        # 刪除按鈕（只有多於一個範圍時才顯示）
        delete_btn = ttk.Button(
            range_frame,
            text="-",
            width=2,
            command=lambda f=range_frame: self._remove_range(f)
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        # 儲存參考
        self.page_ranges.append((first_var, last_var, range_frame, first_entry, last_entry))

        # 更新刪除按鈕顯示狀態
        self._update_delete_buttons()
        self._toggle_mode()

    def _on_ranges_configure(self, event):
        """更新捲動區域"""
        self.ranges_canvas.configure(scrollregion=self.ranges_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """調整內部框架寬度"""
        self.ranges_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """滑鼠滾輪捲動"""
        self.ranges_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _remove_range(self, frame):
        """移除一個頁碼範圍"""
        for i, (first_var, last_var, range_frame, first_entry, last_entry) in enumerate(self.page_ranges):
            if range_frame == frame:
                range_frame.destroy()
                self.page_ranges.pop(i)
                break

        # 更新編號
        self._update_range_numbers()
        self._update_delete_buttons()

    def _update_range_numbers(self):
        """更新範圍編號"""
        for i, (first_var, last_var, range_frame, first_entry, last_entry) in enumerate(self.page_ranges):
            # 找到編號標籤並更新
            for child in range_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    text = child.cget("text")
                    if text.startswith("#"):
                        child.config(text=f"#{i + 1}")
                        break

    def _update_delete_buttons(self):
        """更新刪除按鈕顯示狀態"""
        # 只有一個範圍時隱藏刪除按鈕
        show_delete = len(self.page_ranges) > 1
        for first_var, last_var, range_frame, first_entry, last_entry in self.page_ranges:
            for child in range_frame.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "-":
                    if show_delete:
                        child.pack(side=tk.LEFT, padx=5)
                    else:
                        child.pack_forget()

    def _toggle_mode(self):
        """切換分割模式"""
        mode = self.split_mode_var.get()

        # 頁碼範圍
        range_state = tk.NORMAL if mode == "range" else tk.DISABLED
        for first_var, last_var, range_frame, first_entry, last_entry in self.page_ranges:
            first_entry.config(state=range_state)
            last_entry.config(state=range_state)

        # 每 N 頁
        every_state = tk.NORMAL if mode == "every" else tk.DISABLED
        self.every_n_entry.config(state=every_state)

    def _on_file_selected(self, filename: str):
        """選擇檔案後取得頁數並自動產生輸出檔名"""
        # 自動產生輸出檔名
        output = self.auto_output_filename(filename, "split")
        self.output_var.set(output)

        # 取得頁數
        if self.gs_wrapper:
            try:
                self.total_pages = self.gs_wrapper.get_pdf_page_count(filename)
                self.page_info_label.config(text=f"總頁數: {self.total_pages}")
                # 更新第一個範圍的結束頁碼
                if self.page_ranges:
                    self.page_ranges[0][1].set(str(self.total_pages))
            except Exception:
                self.page_info_label.config(text="總頁數: 無法讀取")
                self.total_pages = 0

    def _on_execute(self):
        """執行分割"""
        input_file = self.input_var.get()
        output_file = self.output_var.get()
        mode = self.split_mode_var.get()

        if not self.validate_input_file(input_file):
            return
        if not self.validate_output_file(output_file):
            return

        if mode == "range":
            self._split_ranges(input_file, output_file)
        elif mode == "every":
            self._split_every_n(input_file, output_file)
        elif mode == "single":
            self._split_single(input_file, output_file)

    def _split_ranges(self, input_file: str, output_file: str):
        """擷取多個頁碼範圍"""
        # 收集所有範圍
        ranges = []
        for i, (first_var, last_var, _, _, _) in enumerate(self.page_ranges):
            try:
                first_page = int(first_var.get())
                last_page = int(last_var.get())
            except ValueError:
                messagebox.showwarning("警告", f"範圍 #{i + 1}: 請輸入有效的頁碼")
                return

            if first_page > last_page:
                messagebox.showwarning("警告", f"範圍 #{i + 1}: 起始頁碼不能大於結束頁碼")
                return

            if first_page < 1:
                messagebox.showwarning("警告", f"範圍 #{i + 1}: 頁碼必須大於 0")
                return

            ranges.append((first_page, last_page))

        if not ranges:
            messagebox.showwarning("警告", "請至少指定一個頁碼範圍")
            return

        num_ranges = len(ranges)
        base, ext = os.path.splitext(output_file)

        def task():
            for idx, (first_page, last_page) in enumerate(ranges):
                # 產生輸出檔名
                if num_ranges == 1:
                    out_file = output_file
                else:
                    out_file = f"{base}_{idx + 1:03d}{ext}"

                # 更新進度
                self._update_progress_safe(
                    idx + 1, num_ranges,
                    f"分割範圍 #{idx + 1} (第 {first_page}-{last_page} 頁)..."
                )

                success, msg = self.gs_wrapper.split_pdf(
                    input_file=input_file,
                    output_file=out_file,
                    first_page=first_page,
                    last_page=last_page
                )

                if not success:
                    return False, msg

            if num_ranges == 1:
                return True, f"已擷取第 {ranges[0][0]}-{ranges[0][1]} 頁"
            else:
                return True, f"已分割為 {num_ranges} 個檔案"

        self.run_in_thread(task)

    def _split_every_n(self, input_file: str, output_file: str):
        """每 N 頁分割"""
        try:
            every_n = int(self.every_n_var.get())
        except ValueError:
            messagebox.showwarning("警告", "請輸入有效的頁數")
            return

        if every_n < 1:
            messagebox.showwarning("警告", "頁數必須大於 0")
            return

        # 取得總頁數
        total_pages = self.gs_wrapper.get_pdf_page_count(input_file)
        if total_pages == 0:
            messagebox.showwarning("警告", "無法讀取 PDF 頁數")
            return

        num_files = (total_pages + every_n - 1) // every_n

        def task():
            base, ext = os.path.splitext(output_file)
            results = []

            for idx, i in enumerate(range(0, total_pages, every_n)):
                first_page = i + 1
                last_page = min(i + every_n, total_pages)
                out_file = f"{base}_{idx + 1:03d}{ext}"

                # 更新進度
                self._update_progress_safe(idx + 1, num_files, f"分割檔案 {idx + 1}/{num_files}...")

                success, msg = self.gs_wrapper.split_pdf(
                    input_file=input_file,
                    output_file=out_file,
                    first_page=first_page,
                    last_page=last_page
                )
                results.append((success, msg))

                if not success:
                    return False, msg

            return True, f"已分割為 {len(results)} 個檔案"

        self.run_in_thread(task)

    def _split_single(self, input_file: str, output_file: str):
        """每頁單獨檔案"""
        total_pages = self.gs_wrapper.get_pdf_page_count(input_file)
        if total_pages == 0:
            messagebox.showwarning("警告", "無法讀取 PDF 頁數")
            return

        def task():
            base, ext = os.path.splitext(output_file)

            for i in range(1, total_pages + 1):
                out_file = f"{base}_{i:03d}{ext}"

                # 更新進度
                self._update_progress_safe(i, total_pages, f"分割第 {i}/{total_pages} 頁...")

                success, msg = self.gs_wrapper.split_pdf(
                    input_file=input_file,
                    output_file=out_file,
                    first_page=i,
                    last_page=i
                )

                if not success:
                    return False, msg

            return True, f"已分割為 {total_pages} 個檔案"

        self.run_in_thread(task)

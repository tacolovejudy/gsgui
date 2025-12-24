# -*- coding: utf-8 -*-
"""
Ghostscript 指令包裝器
封裝各種 Ghostscript 操作
"""

import subprocess
import shutil
import os
from typing import List, Optional, Callable

from .config import PAPER_SIZES, IMAGE_DEVICES


class GhostscriptWrapper:
    """Ghostscript 指令包裝器"""

    def __init__(self):
        self.gs_path = self._find_ghostscript()

    def _find_ghostscript(self) -> str:
        """尋找 Ghostscript 執行檔"""
        # Linux/macOS
        gs = shutil.which("gs")
        if gs:
            return gs

        # Windows - 先檢查 PATH
        for name in ["gswin64c", "gswin32c"]:
            gs = shutil.which(name)
            if gs:
                return gs

        # Windows - 搜尋常見安裝路徑
        import glob
        search_paths = [
            # Program Files 標準安裝路徑
            r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs*\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe",
            # 使用者下載目錄 (便攜版)
            os.path.expanduser(r"~\Downloads\gs*\bin\gswin64c.exe"),
            os.path.expanduser(r"~\Downloads\gs*\gswin64c.exe"),
            os.path.expanduser(r"~\Downloads\ghostscript*\bin\gswin64c.exe"),
        ]

        for pattern in search_paths:
            matches = glob.glob(pattern)
            if matches:
                # 取最新版本 (按名稱排序取最後一個)
                matches.sort()
                return matches[-1]

        raise FileNotFoundError(
            "找不到 Ghostscript，請從以下網址下載安裝：\n"
            "https://ghostscript.com/releases/gsdnld.html\n\n"
            "下載 'Ghostscript X.XX.X for Windows (64 bit)' 並安裝"
        )

    def _run_command_fast(self, args: List[str]) -> tuple[bool, str]:
        """
        快速執行 Ghostscript 指令（無進度追蹤）
        使用 -q 靜默模式，速度最快
        """
        cmd = [self.gs_path, "-q"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def _run_command(
        self,
        args: List[str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
        total_pages: int = 0
    ) -> tuple[bool, str]:
        """
        執行 Ghostscript 指令（含進度追蹤）

        Args:
            args: 命令參數
            progress_callback: 進度回調函數 (current_page, status_text)
            total_pages: 總頁數（用於計算進度）
        """
        cmd = [self.gs_path] + args
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            output_lines = []
            current_page = 0

            for line in process.stdout:
                output_lines.append(line)
                line_stripped = line.strip()

                # 解析頁面處理進度 (Ghostscript 輸出格式: "Page X")
                if line_stripped.startswith("Page "):
                    try:
                        current_page = int(line_stripped.split()[1])
                        if progress_callback:
                            progress_callback(current_page, f"處理第 {current_page} 頁...")
                    except (ValueError, IndexError):
                        pass
                elif progress_callback and line_stripped:
                    # 其他輸出也回報
                    progress_callback(current_page, line_stripped[:50])

            process.wait()
            output = "".join(output_lines)
            return process.returncode == 0, output
        except Exception as e:
            return False, str(e)

    def _run_command_with_progress(
        self,
        args: List[str],
        input_file: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        執行 Ghostscript 指令
        - 有進度回調時：追蹤頁面進度
        - 無進度回調時：使用快速模式
        """
        # 無進度回調時使用快速模式
        if progress_callback is None:
            return self._run_command_fast(args)

        # 取得總頁數
        total_pages = self.get_pdf_page_count(input_file)

        def internal_callback(current_page: int, status: str):
            if total_pages > 0:
                progress_callback(current_page, total_pages, status)

        return self._run_command(args, internal_callback, total_pages)

    def resize_pdf(
        self,
        input_file: str,
        output_file: str,
        paper_size: str = "A4",
        custom_width: Optional[int] = None,
        custom_height: Optional[int] = None,
        fit_page: bool = True,
        dpi: Optional[int] = None,
        pdf_settings: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        調整 PDF 頁面大小

        Args:
            input_file: 輸入 PDF 檔案路徑
            output_file: 輸出 PDF 檔案路徑
            paper_size: 紙張大小 (A4, A3, Letter 等)
            custom_width: 自訂寬度 (points)
            custom_height: 自訂高度 (points)
            fit_page: 是否適應頁面
            dpi: 解析度 (None=不設定，速度最快)
            pdf_settings: PDF 品質設定 (None=不重新壓縮，速度最快)
            progress_callback: 進度回調 (current, total, status)
        """
        if custom_width and custom_height:
            width, height = custom_width, custom_height
        else:
            width, height = PAPER_SIZES.get(paper_size, PAPER_SIZES["A4"])

        args = [
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-dFIXEDMEDIA",
            f"-dDEVICEWIDTHPOINTS={width}",
            f"-dDEVICEHEIGHTPOINTS={height}",
        ]
        # 只有指定時才加入這些參數（不加會快很多）
        if dpi is not None:
            args.append(f"-r{dpi}")
        if pdf_settings is not None:
            args.append(f"-dPDFSETTINGS=/{pdf_settings}")
        if fit_page:
            args.append("-dPDFFitPage")
        args.extend([f"-sOutputFile={output_file}", input_file])

        return self._run_command_with_progress(args, input_file, progress_callback)

    def pdf_to_image(
        self,
        input_file: str,
        output_pattern: str,
        device: str = "PNG",
        dpi: int = 150,
        first_page: Optional[int] = None,
        last_page: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        PDF 轉圖片

        Args:
            input_file: 輸入 PDF 檔案路徑
            output_pattern: 輸出檔案模式 (例如: output_%03d.png)
            device: 輸出裝置 (PNG, JPEG, TIFF)
            dpi: 解析度
            first_page: 起始頁碼
            last_page: 結束頁碼
            progress_callback: 進度回調 (current, total, status)
        """
        device_name = IMAGE_DEVICES.get(device, "png16m")
        args = [
            "-dBATCH",
            "-dNOPAUSE",
            f"-sDEVICE={device_name}",
            f"-r{dpi}",
        ]
        if first_page:
            args.append(f"-dFirstPage={first_page}")
        if last_page:
            args.append(f"-dLastPage={last_page}")
        args.extend([f"-sOutputFile={output_pattern}", input_file])

        return self._run_command_with_progress(args, input_file, progress_callback)

    def merge_pdfs(
        self,
        input_files: List[str],
        output_file: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        合併多個 PDF

        Args:
            input_files: 輸入 PDF 檔案列表
            output_file: 輸出 PDF 檔案路徑
            progress_callback: 進度回調 (current, total, status)
        """
        # 計算總頁數
        total_pages = sum(self.get_pdf_page_count(f) for f in input_files)

        args = [
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={output_file}",
        ] + input_files

        def internal_callback(current_page: int, status: str):
            if progress_callback and total_pages > 0:
                progress_callback(current_page, total_pages, status)

        return self._run_command(args, internal_callback, total_pages)

    def split_pdf(
        self,
        input_file: str,
        output_file: str,
        first_page: int,
        last_page: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        分割 PDF (擷取指定頁面)

        Args:
            input_file: 輸入 PDF 檔案路徑
            output_file: 輸出 PDF 檔案路徑
            first_page: 起始頁碼
            last_page: 結束頁碼
            progress_callback: 進度回調 (current, total, status)
        """
        total_pages = last_page - first_page + 1

        args = [
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            f"-dFirstPage={first_page}",
            f"-dLastPage={last_page}",
            f"-sOutputFile={output_file}",
            input_file,
        ]

        def internal_callback(current_page: int, status: str):
            if progress_callback and total_pages > 0:
                # 調整頁碼顯示 (相對於選取範圍)
                relative_page = current_page - first_page + 1
                progress_callback(relative_page, total_pages, status)

        return self._run_command(args, internal_callback, total_pages)

    def compress_pdf(
        self,
        input_file: str,
        output_file: str,
        pdf_settings: str = "ebook",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        壓縮 PDF

        Args:
            input_file: 輸入 PDF 檔案路徑
            output_file: 輸出 PDF 檔案路徑
            pdf_settings: PDF 品質設定 (screen/ebook/printer/prepress)
            progress_callback: 進度回調 (current, total, status)
        """
        args = [
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFFitPage",
            f"-dPDFSETTINGS=/{pdf_settings}",
            f"-sOutputFile={output_file}",
            input_file,
        ]

        return self._run_command_with_progress(args, input_file, progress_callback)

    def get_pdf_page_count(self, input_file: str) -> int:
        """取得 PDF 頁數"""
        # 將路徑轉換為 PostScript 格式（處理反斜線和特殊字元）
        ps_path = input_file.replace("\\", "/")

        # 注意：_run_command_fast 會自動加 -q，所以這裡不需要再加
        args = [
            "-dNODISPLAY",
            "-dNOSAFER",
            "-c",
            f"({ps_path}) (r) file runpdfbegin pdfpagecount = quit"
        ]
        success, output = self._run_command_fast(args)
        if success:
            try:
                return int(output.strip())
            except ValueError:
                return 0
        return 0

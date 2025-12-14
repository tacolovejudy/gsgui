# -*- coding: utf-8 -*-
"""
圖片轉 PDF 轉換器
使用 Pillow 將圖片轉換為 PDF
"""

import os
from typing import List, Optional, Callable
from PIL import Image


class ImageConverter:
    """圖片轉 PDF 轉換器"""

    @staticmethod
    def images_to_pdf(
        image_files: List[str],
        output_file: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        將多個圖片轉換為單一 PDF

        Args:
            image_files: 圖片檔案路徑列表
            output_file: 輸出 PDF 檔案路徑
            progress_callback: 進度回調 (current, total, status)

        Returns:
            (成功與否, 訊息)
        """
        try:
            if not image_files:
                return False, "沒有選擇圖片檔案"

            # 驗證所有檔案是否存在
            for img_file in image_files:
                if not os.path.exists(img_file):
                    return False, f"檔案不存在: {img_file}"

            # 載入並轉換圖片
            images = []
            total = len(image_files)

            for i, img_file in enumerate(image_files):
                if progress_callback:
                    progress_callback(i + 1, total, f"載入圖片 {i + 1}/{total}...")

                try:
                    img = Image.open(img_file)
                    # 轉換為 RGB 模式（PDF 需要）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    # 關閉已開啟的圖片
                    for opened_img in images:
                        opened_img.close()
                    return False, f"無法載入圖片 {img_file}: {str(e)}"

            # 儲存為 PDF
            if progress_callback:
                progress_callback(total, total, "儲存 PDF...")

            if len(images) == 1:
                images[0].save(output_file, "PDF", resolution=100.0)
            else:
                images[0].save(
                    output_file,
                    "PDF",
                    resolution=100.0,
                    save_all=True,
                    append_images=images[1:]
                )

            # 關閉所有圖片
            for img in images:
                img.close()

            if progress_callback:
                progress_callback(total, total, "完成")

            return True, f"成功轉換 {len(image_files)} 張圖片為 PDF"

        except Exception as e:
            return False, f"轉換失敗: {str(e)}"

    @staticmethod
    def images_to_pdfs_batch(
        image_files: List[str],
        output_pattern: str,
        images_per_pdf: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> tuple[bool, str]:
        """
        將圖片分組轉換為多個 PDF（每 N 張圖片一個 PDF）

        Args:
            image_files: 圖片檔案路徑列表
            output_pattern: 輸出檔案模式（例如: output_{:03d}.pdf）
            images_per_pdf: 每個 PDF 包含的圖片數量
            progress_callback: 進度回調 (current, total, status)

        Returns:
            (成功與否, 訊息)
        """
        try:
            if not image_files:
                return False, "沒有選擇圖片檔案"

            if images_per_pdf < 1:
                return False, "每個 PDF 的圖片數量必須大於 0"

            # 計算總共需要生成多少個 PDF
            total_pdfs = (len(image_files) + images_per_pdf - 1) // images_per_pdf
            total_images = len(image_files)
            processed_images = 0

            created_files = []

            # 分組處理
            for pdf_index in range(total_pdfs):
                start_idx = pdf_index * images_per_pdf
                end_idx = min(start_idx + images_per_pdf, len(image_files))
                batch_images = image_files[start_idx:end_idx]

                # 生成輸出檔名
                if total_pdfs == 1:
                    # 只有一個 PDF 時，使用原始檔名（去掉編號模式）
                    output_file = output_pattern.replace("_{:03d}", "").replace("_{}", "")
                else:
                    # 多個 PDF 時，加上編號
                    if "{:03d}" in output_pattern:
                        output_file = output_pattern.format(pdf_index + 1)
                    elif "{}" in output_pattern:
                        output_file = output_pattern.format(pdf_index + 1)
                    else:
                        # 如果模式中沒有格式化標記，自動添加
                        base, ext = os.path.splitext(output_pattern)
                        output_file = f"{base}_{pdf_index + 1:03d}{ext}"

                # 轉換當前批次
                def batch_progress(current, total, status):
                    overall_current = processed_images + current
                    if progress_callback:
                        progress_callback(
                            overall_current,
                            total_images,
                            f"PDF {pdf_index + 1}/{total_pdfs}: {status}"
                        )

                success, message = ImageConverter.images_to_pdf(
                    batch_images,
                    output_file,
                    batch_progress
                )

                if not success:
                    return False, f"PDF {pdf_index + 1} 轉換失敗: {message}"

                created_files.append(output_file)
                processed_images += len(batch_images)

            return True, f"成功轉換 {total_images} 張圖片為 {total_pdfs} 個 PDF 檔案"

        except Exception as e:
            return False, f"批次轉換失敗: {str(e)}"

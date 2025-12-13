# Ghostscript GUI

一個跨平台的 Ghostscript 圖形介面工具，提供常用的 PDF 處理功能。

## 功能特色

- **頁面調整** - 調整 PDF 頁面大小（A4、A3、Letter 等），支援自訂尺寸
- **轉換圖片** - 將 PDF 轉換為 PNG、JPEG、TIFF 圖片
- **合併 PDF** - 將多個 PDF 檔案合併為一個
- **分割 PDF** - 擷取指定頁碼範圍，支援多範圍分割
- **壓縮 PDF** - 壓縮 PDF 檔案大小，提供多種品質選項

## 系統需求

- Python 3.8+
- Ghostscript
- Tkinter（Python 標準庫）

## 安裝

### Windows

1. 下載並安裝 [Ghostscript](https://ghostscript.com/releases/gsdnld.html)
2. 下載本程式或 clone 此 repo：
   ```bash
   git clone https://github.com/tacolovejudy/gsgui.git
   cd gsgui
   ```
3. 執行程式：
   ```bash
   python main.py
   ```

### Linux (Ubuntu/Debian)

**方法一：使用 DEB 安裝包**

從 [Releases](https://github.com/tacolovejudy/gsgui/releases) 下載 `.deb` 檔案，然後：
```bash
sudo dpkg -i gsgui_*.deb
sudo apt-get install -f  # 安裝相依套件
```

**方法二：從原始碼執行**
```bash
# 安裝相依套件
sudo apt-get install ghostscript python3-tk fonts-noto-cjk

# 下載並執行
git clone https://github.com/tacolovejudy/gsgui.git
cd gsgui
python3 main.py
```

### macOS

```bash
# 使用 Homebrew 安裝 Ghostscript
brew install ghostscript

# 下載並執行
git clone https://github.com/tacolovejudy/gsgui.git
cd gsgui
python3 main.py
```

## 使用說明

### 頁面調整
1. 選擇輸入 PDF 檔案
2. 選擇目標紙張大小或自訂尺寸
3. 選擇縮放模式（適應頁面/固定大小）
4. 如需壓縮，勾選「重新壓縮」並設定解析度和品質
5. 點擊「執行」

### 轉換圖片
1. 選擇輸入 PDF 檔案
2. 選擇輸出格式（PNG/JPEG/TIFF）
3. 設定解析度（DPI）
4. 可選擇只轉換特定頁碼範圍
5. 點擊「執行」

### 合併 PDF
1. 點擊「新增檔案」加入要合併的 PDF
2. 使用「上移」「下移」調整順序
3. 設定輸出檔案路徑
4. 點擊「執行」

### 分割 PDF
1. 選擇輸入 PDF 檔案
2. 選擇分割模式：
   - **擷取頁碼範圍**：指定一個或多個頁碼範圍（點擊「+ 新增範圍」可加入更多）
   - **每 N 頁分割**：每 N 頁分割成一個檔案
   - **每頁單獨檔案**：每頁分割成獨立檔案
3. 設定輸出檔案路徑（多檔案時自動加上編號）
4. 點擊「執行」

### 壓縮 PDF
1. 選擇輸入 PDF 檔案
2. 選擇壓縮等級：
   - **screen** - 72 dpi，最小檔案，適合螢幕瀏覽
   - **ebook** - 150 dpi，中等品質，適合電子書
   - **printer** - 300 dpi，高品質，適合列印
   - **prepress** - 300 dpi，最高品質，適合出版
3. 點擊「執行」

## 授權

MIT License

## 致謝

本專案使用 [Ghostscript](https://www.ghostscript.com/) 進行 PDF 處理。

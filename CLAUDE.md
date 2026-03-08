# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OCR-enabled image-to-PDF conversion and merge tool with Japanese and English OCR support. Converts directories of images (JPEG/PNG) into searchable PDFs and combines them into a single file. Also includes PDF size-based splitting functionality.

## Commands

### Environment Setup
```bash
pipenv install
```

### ndlocr-lite Setup (required, run once)
```bash
git clone https://github.com/ndl-lab/ndlocr-lite
cd ndlocr-lite && pip install -r requirements.txt && cd ..
```

### Running the Tool
```bash
# OCR and PDF merge (command line) — uses ./ndlocr-lite/src by default
pipenv run python ocr_merge.py -i <image_directory> -o <output.pdf>

# Specify ndlocr-lite/src explicitly
pipenv run python ocr_merge.py -i <image_directory> -o <output.pdf> --ndlocr-src ./ndlocr-lite/src

# Or set via environment variable
export NDLOCR_LITE_SRC=./ndlocr-lite/src
pipenv run python ocr_merge.py -i <image_directory> -o <output.pdf>

# PDF split by size (command line)
pipenv run python pdf_split.py -i <input.pdf> -s <max_size_mb> -o <output_dir>

# Unified GUI (feature selection between OCR merge and PDF split)
pipenv run python pdf_split_gui.py

# OCR merge GUI only
pipenv run python ocr_merge_gui.py

# Build standalone executables (macOS)
pipenv run pyinstaller --onefile --windowed ocr_merge_gui.py
pipenv run pyinstaller --onefile --windowed pdf_split_gui.py
```

### OCR Comparison Tool
```bash
# Compare pytesseract (optional) vs ndlocr-lite on a single image
pipenv run python compare_ocr.py -i <image.jpg> --ndlocr-src ./ndlocr-lite/src

# Compare all images in a directory
pipenv run python compare_ocr.py -d <image_directory> --ndlocr-src ./ndlocr-lite/src

# Output side-by-side HTML
pipenv run python compare_ocr.py -i <image.jpg> --ndlocr-src ./ndlocr-lite/src --output result.html
```

## Architecture

### Core Components

1. **ocr_merge.py**: Core OCR and PDF merge logic
   - Image file discovery (JPG/JPEG/PNG) with alphabetical sort
   - OCR via ndlocr-lite (subprocess call to `ocr.py`) → JSON result → reportlab で Searchable PDF 生成 → merged with PyPDF2.PdfMerger
   - 起動時に ndlocr-lite の存在チェック（`ocr.py` がなければ即時エラー終了）
   - `--ndlocr-src` 引数でパス指定可（省略時: 環境変数 `NDLOCR_LITE_SRC` → `./ndlocr-lite/src`）
   - 不可視テキスト（renderMode=3）を画像上に重ねて Searchable PDF を実現

2. **ocr_merge_gui.py**: TkEasyGUI wrapper for ocr_merge.py
   - Runs ocr_merge.py as subprocess with real-time stdout display via threading

3. **pdf_split.py**: PDF size-based splitting
   - Splits PDF under a size limit (default **25MB**) using PyPDF2 PdfReader/PdfWriter
   - Writes temp files per part to check size before committing

4. **pdf_split_gui.py**: Unified GUI entry point
   - Prompts user to choose between "PDF分割" or "OCR結合" at startup
   - For OCR結合: imports and calls `ocr_merge_gui.main()` directly
   - For PDF分割: runs pdf_split.py as subprocess

5. **screenshot.applescript**: AppleScript for automated Kindle screenshot capture
   - Activates Kindle app, captures screenshots page by page with keyboard navigation
   - Configurable: `DEFAULT_SUBDIR`, `DEFAULT_BASEDIR`, `DEFAULT_PAGES`, page direction (left/right)
   - Output: zero-padded PNG files (`p001.png`, `p002.png`, ...) in the configured save path

### Key Design Patterns

- GUI layers are thin wrappers: they invoke CLI scripts as subprocesses and display stdout/stderr in a Multiline widget
- No tests exist in this project

## Configuration Notes

- Python 3.12 (specified in Pipfile)
- OCR engine: ndlocr-lite（国立国会図書館製、縦書き高精度）。pytesseract は廃止済み
- `pdf_split.py` default max size: 25MB (CLI help text says 30 but code default is 25)
- `screenshot.applescript` source file is Shift-JIS encoded; comments may appear garbled in UTF-8 editors

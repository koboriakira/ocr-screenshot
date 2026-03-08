# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OCR-enabled image-to-PDF conversion and merge tool with Japanese and English OCR support. Converts directories of images (JPEG/PNG) into searchable PDFs and combines them into a single file. Also includes PDF size-based splitting functionality.

## Commands

### Environment Setup
```bash
pipenv install
```

### Running the Tool
```bash
# OCR and PDF merge (command line)
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
# Compare pytesseract vs ndlocr-lite on a single image
pipenv run python compare_ocr.py -i <image.jpg> --ndlocr-src ./ndlocr-lite/src

# Compare all images in a directory
pipenv run python compare_ocr.py -d <image_directory> --ndlocr-src ./ndlocr-lite/src

# Output side-by-side HTML
pipenv run python compare_ocr.py -i <image.jpg> --ndlocr-src ./ndlocr-lite/src --output result.html

# ndlocr-lite setup (run once)
# git clone https://github.com/ndl-lab/ndlocr-lite
# cd ndlocr-lite && pip install -r requirements.txt && cd ..
```

### External Dependencies
- Tesseract OCR must be installed separately:
  - macOS: `brew install tesseract tesseract-lang`
  - Linux: `sudo apt install tesseract-ocr libtesseract-dev tesseract-ocr-jpn`

## Architecture

### Core Components

1. **ocr_merge.py**: Core OCR and PDF merge logic
   - Image file discovery (JPG/JPEG/PNG) with alphabetical sort
   - OCR via pytesseract (`jpn+eng`) → individual PDF per image → merged with PyPDF2.PdfMerger
   - `auto_rotate_image()` exists but is **intentionally disabled** in `image_to_pdf_with_ocr()` (the `rotate` arg is ignored)
   - `--no-rotate` flag is accepted but has no effect

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
- OCR languages: `jpn+eng`
- `pdf_split.py` default max size: 25MB (CLI help text says 30 but code default is 25)
- `screenshot.applescript` source file is Shift-JIS encoded; comments may appear garbled in UTF-8 editors

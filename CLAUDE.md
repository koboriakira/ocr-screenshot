# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OCR-enabled image-to-PDF conversion and merge tool with Japanese and English OCR support. Converts directories of images (JPEG/PNG) into searchable PDFs and combines them into a single file.

## Commands

### Environment Setup
```bash
# Install dependencies with pipenv
pipenv install

# Install additional GUI dependencies
pipenv install TkEasyGUI

# Install build dependencies
pipenv install pyinstaller
```

### Running the Tool
```bash
# OCR and PDF merge (command line)
pipenv run python ocr_merge.py -i <image_directory> -o <output.pdf>

# PDF split by size (command line)
pipenv run python pdf_split.py -i <input.pdf> -s <max_size_mb> -o <output_dir>

# GUI version (OCR merge)
pipenv run python ocr_merge_gui.py

# GUI version (PDF split with feature selection)
pipenv run python pdf_split_gui.py

# Build standalone executables (macOS)
pipenv run pyinstaller --onefile --windowed ocr_merge_gui.py
pipenv run pyinstaller --onefile --windowed pdf_split_gui.py
```

### External Dependencies
- Tesseract OCR must be installed separately:
  - macOS: `brew install tesseract tesseract-lang`
  - Linux: `sudo apt install tesseract-ocr libtesseract-dev tesseract-ocr-jpn`

## Architecture

### Core Components

1. **ocr_merge.py**: Core OCR and PDF merge functionality
   - Image preprocessing with OpenCV auto-rotation
   - OCR processing using pytesseract with Japanese+English language support
   - PDF generation and merging using PyPDF2
   - Command-line interface with argparse

2. **ocr_merge_gui.py**: TkEasyGUI-based GUI wrapper
   - Form-based input for directory selection and output naming
   - Subprocess execution of ocr_merge.py with real-time output display
   - Progress monitoring through threading

3. **pdf_split.py**: PDF size-based splitting functionality
   - Splits large PDFs into smaller files under specified size limit (default 30MB)
   - Uses PyPDF2 for PDF reading and writing
   - Intelligent page allocation to maximize file size usage while staying under limit
   - Command-line interface with size and directory options

4. **pdf_split_gui.py**: GUI wrapper for PDF splitting
   - Feature selection between OCR merge and PDF split
   - Form-based input for PDF file selection and size limits
   - Real-time progress display through subprocess execution

5. **screenshot.applescript**: AppleScript for automated Kindle screenshot capture
   - Configurable page navigation and screenshot saving
   - Supports left/right page turning with keyboard simulation

### Key Design Patterns

- **Separation of Concerns**: GUI acts as a thin wrapper around core CLI functionality
- **Pipeline Processing**: Images → Individual OCR PDFs → Merged final PDF
- **Error Handling**: Comprehensive error reporting through GUI output display
- **Temporary File Management**: Uses tempfile module for intermediate PDF storage

### Image Processing Pipeline

1. Image file discovery (JPEG/PNG) with alphabetical sorting
2. Optional auto-rotation correction using OpenCV contour detection
3. OCR processing with pytesseract (Japanese+English)
4. Individual PDF generation per image
5. PDF merging using PyPDF2.PdfMerger
6. Cleanup of temporary files

## Configuration

- Default Python version: 3.12+ (specified in Pipfile)
- OCR languages: Japanese + English (`jpn+eng`)
- Supported image formats: JPG, JPEG, PNG
- Auto-rotation can be disabled with `--no-rotate` flag

## Build and Distribution

- Uses PyInstaller for standalone executable creation
- Requires ocr_merge.py to be bundled with GUI executable
- macOS app bundle generation supported
- Tesseract must be installed separately on target systems
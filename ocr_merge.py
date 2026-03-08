import os
import glob
import argparse
import tempfile
import shutil
from PIL import Image
import pytesseract
from PyPDF2 import PdfMerger


def find_image_files(directory: str) -> list[str]:
    """指定ディレクトリから画像ファイルを取得して昇順ソートで返す"""
    exts = ('*.jpg', '*.jpeg', '*.png')
    files: list[str] = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(directory, ext)))
    files.sort()
    return files


def image_to_pdf_with_ocr(image_path: str, pdf_path: str, lang: str = 'jpn+eng') -> None:
    """画像をOCR付きPDFに変換して保存する"""
    image = Image.open(image_path)
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=lang, extension='pdf')
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)


def merge_pdfs(pdf_paths: list[str], output_path: str) -> None:
    """複数のPDFファイルを1つに結合する"""
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def main() -> None:
    parser = argparse.ArgumentParser(description='画像をOCR付きPDFに変換し結合するツール')
    parser.add_argument('-i', '--input_dir', required=True, help='画像ファイルのディレクトリ')
    parser.add_argument('-o', '--output', required=True, help='出力PDFファイル名')
    args = parser.parse_args()

    files = find_image_files(args.input_dir)
    if not files:
        print('画像ファイルが見つかりません')
        return

    temp_dir = tempfile.mkdtemp()
    pdf_paths: list[str] = []
    try:
        total = len(files)
        print(f'処理開始: {total}枚の画像')
        for idx, img_path in enumerate(files):
            pdf_path = os.path.join(temp_dir, f'{idx:04d}.pdf')
            print(f'[{idx+1}/{total}] OCR処理中: {os.path.basename(img_path)}')
            image_to_pdf_with_ocr(img_path, pdf_path)
            print(f'[{idx+1}/{total}] 完了: {os.path.basename(img_path)}')
            pdf_paths.append(pdf_path)
        print('PDF結合中...')
        merge_pdfs(pdf_paths, args.output)
        print(f'完了: {args.output}')
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()

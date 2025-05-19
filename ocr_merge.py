import os
import glob
import argparse
import tempfile
import shutil
from PIL import Image
import pytesseract
from PyPDF2 import PdfMerger
import cv2


def auto_rotate_image(image_path):
    # OpenCVで画像を読み込み
    img = cv2.imread(image_path)
    if img is None:
        return image_path  # 読み込み失敗時はそのまま
    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # しきい値処理
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # 輪郭検出
    coords = cv2.findNonZero(thresh)
    angle = 0
    if coords is not None:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        # 回転
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        temp_rotated_path = image_path + '_rotated.jpg'
        cv2.imwrite(temp_rotated_path, rotated)
        return temp_rotated_path
    return image_path


def image_to_pdf_with_ocr(image_path, pdf_path, lang='jpn+eng', rotate=True):
    # 回転補正機能を完全に無効化（rotate引数は無視）
    image = Image.open(image_path)
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=lang, extension='pdf')
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)


def main():
    parser = argparse.ArgumentParser(description='画像をOCR付きPDFに変換し結合するツール')
    parser.add_argument('-i', '--input_dir', required=True, help='画像ファイルのディレクトリ')
    parser.add_argument('-o', '--output', required=True, help='出力PDFファイル名')
    parser.add_argument('--no-rotate', action='store_true', help='自動回転補正を無効化')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_pdf = args.output
    rotate = not args.no_rotate

    # 画像ファイル取得
    exts = ('*.jpg', '*.jpeg', '*.png')
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(input_dir, ext)))
    files.sort()
    if not files:
        print('画像ファイルが見つかりません')
        return

    temp_dir = tempfile.mkdtemp()
    pdf_paths = []
    try:
        total = len(files)
        print(f'処理開始: {total}枚の画像')
        for idx, img_path in enumerate(files):
            pdf_path = os.path.join(temp_dir, f'{idx:04d}.pdf')
            print(f'[{idx+1}/{total}] OCR処理中: {os.path.basename(img_path)}')
            image_to_pdf_with_ocr(img_path, pdf_path, rotate=rotate)
            print(f'[{idx+1}/{total}] 完了: {os.path.basename(img_path)}')
            pdf_paths.append(pdf_path)
        print('PDF結合中...')
        merger = PdfMerger()
        for pdf in pdf_paths:
            merger.append(pdf)
        merger.write(output_pdf)
        merger.close()
        print(f'完了: {output_pdf}')
    finally:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()

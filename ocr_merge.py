import os
import sys
import glob
import json
import argparse
import tempfile
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))


def find_image_files(directory: str) -> list[str]:
    """指定ディレクトリから画像ファイルを取得して昇順ソートで返す"""
    exts = ('*.jpg', '*.jpeg', '*.png')
    files: list[str] = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(directory, ext)))
    files.sort()
    return files


def _resolve_ndlocr_src(ndlocr_src: str | None) -> Path:
    """ndlocr-lite/src のパスを解決する"""
    if ndlocr_src:
        return Path(ndlocr_src).resolve()
    env_val = os.environ.get('NDLOCR_LITE_SRC')
    if env_val:
        return Path(env_val).resolve()
    script_dir = Path(__file__).parent
    default = script_dir / 'ndlocr-lite' / 'src'
    return default.resolve()


def image_to_pdf_with_ocr(image_path: str, pdf_path: str, ndlocr_src: Path) -> None:
    """ndlocr-lite で OCR し、searchable PDF を生成する"""
    ocr_py = ndlocr_src / 'ocr.py'
    if not ocr_py.exists():
        raise FileNotFoundError(f'ndlocr-lite の ocr.py が見つかりません: {ocr_py}')

    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [sys.executable, str(ocr_py), '--sourceimg', image_path, '--output', tmp_dir],
            cwd=str(ndlocr_src),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f'ndlocr-lite 実行エラー:\n{result.stderr}', file=sys.stderr)
            sys.exit(1)

        stem = Path(image_path).stem
        json_path = Path(tmp_dir) / f'{stem}.json'
        if not json_path.exists():
            # 出力ファイルが見つからない場合、tmpディレクトリの内容を確認
            json_files = list(Path(tmp_dir).glob('*.json'))
            if json_files:
                json_path = json_files[0]
            else:
                raise FileNotFoundError(f'OCR 結果 JSON が見つかりません: {json_path}')

        with open(json_path, encoding='utf-8') as f:
            ocr_data = json.load(f)

        img = Image.open(image_path)
        img_w, img_h = img.size

        c = canvas.Canvas(pdf_path, pagesize=(img_w, img_h))
        c.drawImage(ImageReader(image_path), 0, 0, width=img_w, height=img_h)

        c.setFont('HeiseiMin-W3', 12)

        for block_list in ocr_data.get('contents', []):
            for item in block_list:
                text = item.get('text', '').strip()
                if not text:
                    continue
                bb = item.get('boundingBox', [])
                if len(bb) < 4:
                    continue
                # boundingBox: [[x1,y1],[x1,y1+h],[x1+w,y1],[x1+w,y1+h]]
                xs = [pt[0] for pt in bb]
                ys = [pt[1] for pt in bb]
                x1 = min(xs)
                y1 = min(ys)
                x2 = max(xs)
                y2 = max(ys)
                w = x2 - x1
                h = y2 - y1
                font_size = max(h, 4)

                # PDF 座標は左下原点 (Y軸反転)
                y_pdf = img_h - y1 - h

                c.setFont('HeiseiMin-W3', font_size)
                c.setFillColorRGB(0, 0, 0, alpha=0)
                # renderMode=3 で不可視テキスト
                c.setTextRenderMode(3)
                c.drawString(x1, y_pdf, text)

        c.save()


def merge_pdfs(pdf_paths: list[str], output_path: str) -> None:
    """複数のPDFファイルを1つに結合する"""
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def main() -> None:
    parser = argparse.ArgumentParser(description='画像をOCR付きPDFに変換し結合するツール（ndlocr-lite使用）')
    parser.add_argument('-i', '--input_dir', required=True, help='画像ファイルのディレクトリ')
    parser.add_argument('-o', '--output', required=True, help='出力PDFファイル名')
    parser.add_argument(
        '--ndlocr-src',
        default=None,
        help='ndlocr-lite/src のパス（省略時: 環境変数 NDLOCR_LITE_SRC → スクリプト隣の ./ndlocr-lite/src）',
    )
    args = parser.parse_args()

    ndlocr_src = _resolve_ndlocr_src(args.ndlocr_src)
    ocr_py = ndlocr_src / 'ocr.py'
    if not ocr_py.exists():
        print(f'エラー: ndlocr-lite が見つかりません: {ocr_py}', file=sys.stderr)
        print('ndlocr-lite をセットアップしてください:', file=sys.stderr)
        print('  git clone https://github.com/ndl-lab/ndlocr-lite', file=sys.stderr)
        print('  cd ndlocr-lite && pip install -r requirements.txt', file=sys.stderr)
        sys.exit(1)
    print(f'ndlocr-lite src: {ndlocr_src}')

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
            image_to_pdf_with_ocr(img_path, pdf_path, ndlocr_src)
            print(f'[{idx+1}/{total}] 完了: {os.path.basename(img_path)}')
            pdf_paths.append(pdf_path)
        print('PDF結合中...')
        merge_pdfs(pdf_paths, args.output)
        print(f'完了: {args.output}')
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()

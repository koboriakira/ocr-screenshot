#!/usr/bin/env python3
"""
Kindle スクリーンショット → OCR → PDF 変換エージェント

使い方:
    pipenv run python kindle_agent.py
"""
import os
import re
import sys
import subprocess

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_APPLESCRIPT_PATH = os.path.join(_SCRIPT_DIR, 'screenshot.applescript')
_OCR_SCRIPT = os.path.join(_SCRIPT_DIR, 'ocr_merge.py')
_SPLIT_SCRIPT = os.path.join(_SCRIPT_DIR, 'pdf_split.py')
_DEFAULT_BASEDIR = '/Users/koboriakira/Documents/KindleOCR'
_DEFAULT_MAX_SIZE_MB = 25.0


def _read_applescript() -> str:
    with open(_APPLESCRIPT_PATH, 'r', encoding='shift_jis', errors='replace') as f:
        return f.read()


def _write_applescript(content: str) -> None:
    with open(_APPLESCRIPT_PATH, 'w', encoding='shift_jis', errors='replace') as f:
        f.write(content)


def edit_applescript(book_name: str, num_pages: int, page_direction: str) -> None:
    """AppleScriptの設定値を書き換える。"""
    content = _read_applescript()

    # DEFAULT_SUBDIR（書籍名 = 保存サブディレクトリ）
    content = re.sub(
        r'property DEFAULT_SUBDIR : ".*?"',
        f'property DEFAULT_SUBDIR : "{book_name}"',
        content,
    )

    # DEFAULT_PAGES
    content = re.sub(
        r'property DEFAULT_PAGES : \d+',
        f'property DEFAULT_PAGES : {num_pages}',
        content,
    )

    # pagedir（ページ送り方向）
    page_const = 'PAGE_LEFT' if page_direction == 'left' else 'PAGE_RIGHT'
    content = re.sub(
        r'set pagedir to PAGE_\w+',
        f'set pagedir to {page_const}',
        content,
    )

    _write_applescript(content)
    print(f'[OK] screenshot.applescript を更新しました')
    print(f'     書籍名: {book_name}')
    print(f'     ページ数: {num_pages}')
    print(f'     ページ送り: {"左（←キー）" if page_direction == "left" else "右（→キー）"}')


def run_ocr_merge(image_dir: str, output_pdf: str) -> None:
    """OCR → PDF 変換を実行する。"""
    print(f'\n[OCR] 画像を PDF に変換中...')
    print(f'      入力: {image_dir}')
    print(f'      出力: {output_pdf}')
    cmd = [sys.executable, _OCR_SCRIPT, '-i', image_dir, '-o', output_pdf]
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print(f'[ERROR] OCR変換に失敗しました (終了コード: {result.returncode})')
        sys.exit(1)
    print(f'[OK] PDF 変換完了: {output_pdf}')


def run_pdf_split(input_pdf: str, output_dir: str, max_size_mb: float) -> list[str]:
    """PDF を指定サイズ以下に分割する。"""
    print(f'\n[SPLIT] PDF を {max_size_mb}MB 以下に分割中...')
    cmd = [sys.executable, _SPLIT_SCRIPT, '-i', input_pdf, '-o', output_dir, '-s', str(max_size_mb)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'[ERROR] PDF分割に失敗しました:\n{result.stderr}')
        sys.exit(1)

    # 出力ファイル一覧を収集
    import glob
    basename = os.path.splitext(os.path.basename(input_pdf))[0]
    parts = sorted(glob.glob(os.path.join(output_dir, f'{basename}_part*.pdf')))
    print(f'[OK] 分割完了: {len(parts)} ファイル')
    for p in parts:
        size_mb = os.path.getsize(p) / (1024 * 1024)
        print(f'     {os.path.basename(p)} ({size_mb:.1f} MB)')
    return parts


def prompt(message: str, default: str = '') -> str:
    if default:
        answer = input(f'{message} [{default}]: ').strip()
        return answer if answer else default
    else:
        while True:
            answer = input(f'{message}: ').strip()
            if answer:
                return answer
            print('  入力が必要です。')


def main() -> None:
    print('=' * 60)
    print('  Kindle スクリーンショット → OCR → PDF エージェント')
    print('=' * 60)

    # --- Step 1: 書籍情報を入力 ---
    print('\n【Step 1】書籍情報を入力してください\n')

    book_name = prompt('書籍名（保存ディレクトリ名になります）')
    num_pages_str = prompt('ページ数（スクリーンショットの枚数）')
    try:
        num_pages = int(num_pages_str)
    except ValueError:
        print('[ERROR] ページ数は整数で入力してください')
        sys.exit(1)

    direction_input = prompt('ページ送り方向 (left / right)', default='left')
    if direction_input not in ('left', 'right'):
        print('[ERROR] left または right を入力してください')
        sys.exit(1)

    max_size_str = prompt(f'PDF最大サイズ (MB)', default=str(_DEFAULT_MAX_SIZE_MB))
    try:
        max_size_mb = float(max_size_str)
    except ValueError:
        print('[ERROR] MB は数値で入力してください')
        sys.exit(1)

    save_dir = os.path.join(_DEFAULT_BASEDIR, book_name)
    output_pdf = os.path.join(_DEFAULT_BASEDIR, f'{book_name}.pdf')

    print(f'\n  スクリーンショット保存先: {save_dir}')
    print(f'  PDF出力先:               {output_pdf}')
    confirm = prompt('\nこの設定で進めますか？ (y/n)', default='y')
    if confirm.lower() != 'y':
        print('中断しました。')
        sys.exit(0)

    # --- Step 2: AppleScript を編集 ---
    print('\n【Step 2】AppleScript を編集します\n')
    edit_applescript(book_name, num_pages, direction_input)

    # --- Step 3: ユーザーにスクリーンショット実行を促す ---
    print('\n【Step 3】スクリーンショットを撮影してください\n')
    print('  以下の手順で実行してください:')
    print('  1. Kindle アプリを開き、対象の書籍の最初のページを表示する')
    print('  2. 別のターミナルで以下のコマンドを実行する:')
    print()
    print(f'     osascript {_APPLESCRIPT_PATH}')
    print()
    print('  3. スクリーンショットが完了するまで待つ')
    print(f'     （{save_dir} に p001.png, p002.png, ... が保存されます）')
    print()
    input('  完了したら Enter を押してください...')

    # 保存先ディレクトリの存在確認
    if not os.path.isdir(save_dir):
        print(f'[ERROR] 保存先ディレクトリが見つかりません: {save_dir}')
        print('  スクリーンショットが正常に完了したか確認してください。')
        sys.exit(1)

    import glob
    images = sorted(glob.glob(os.path.join(save_dir, 'p*.png')))
    print(f'[OK] {len(images)} 枚の画像を確認しました')

    # --- Step 4: OCR → PDF 変換 ---
    print('\n【Step 4】OCR & PDF 変換\n')
    run_ocr_merge(save_dir, output_pdf)

    # --- Step 5: PDF 分割 ---
    pdf_size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
    print(f'\n  生成されたPDFのサイズ: {pdf_size_mb:.1f} MB')

    if pdf_size_mb <= max_size_mb:
        print(f'[OK] {max_size_mb}MB 以下なので分割は不要です')
        split_files = [output_pdf]
    else:
        print(f'\n【Step 5】PDF 分割 ({max_size_mb}MB 以下に分割)\n')
        split_dir = os.path.join(_DEFAULT_BASEDIR, book_name + '_split')
        os.makedirs(split_dir, exist_ok=True)
        split_files = run_pdf_split(output_pdf, split_dir, max_size_mb)

    # --- 完了 ---
    print('\n' + '=' * 60)
    print('  完了！')
    print('=' * 60)
    print('\n生成されたファイル:')
    for f in split_files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f'  {f} ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()

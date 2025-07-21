import os
import argparse
import tempfile
from PyPDF2 import PdfReader, PdfWriter


def get_file_size_mb(filepath):
    """ファイルサイズをMB単位で取得"""
    return os.path.getsize(filepath) / (1024 * 1024)


def split_pdf_by_size(input_pdf_path, max_size_mb=25, output_dir=None):
    """PDFをファイルサイズ制限で分割する

    Args:
        input_pdf_path: 入力PDFファイルのパス
        max_size_mb: 最大ファイルサイズ（MB）
        output_dir: 出力ディレクトリ（Noneの場合は入力ファイルと同じディレクトリ）

    Returns:
        分割されたPDFファイルのパスのリスト
    """
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_pdf_path}")

    # 出力ディレクトリの設定
    if output_dir is None:
        output_dir = os.path.dirname(input_pdf_path)

    # 入力ファイル名から拡張子を除いた名前を取得
    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]

    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    print(f"入力PDF: {input_pdf_path}")
    print(f"総ページ数: {total_pages}")
    print(f"元ファイルサイズ: {get_file_size_mb(input_pdf_path):.2f}MB")
    print(f"分割サイズ制限: {max_size_mb}MB")

    output_files = []
    part_num = 1
    current_writer = PdfWriter()
    current_pages = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        for page_num in range(total_pages):
            # ページを追加
            current_writer.add_page(reader.pages[page_num])
            current_pages += 1

            # 一時ファイルに保存してサイズをチェック
            temp_path = os.path.join(temp_dir, f"temp_part_{part_num}.pdf")
            with open(temp_path, 'wb') as temp_file:
                current_writer.write(temp_file)

            temp_size_mb = get_file_size_mb(temp_path)

            # サイズ制限に達した場合、または最後のページの場合
            should_split = (temp_size_mb >= max_size_mb) or (page_num == total_pages - 1)

            if should_split:
                # 制限を超えていて複数ページがある場合は、最後のページを除いて保存
                if temp_size_mb >= max_size_mb and current_pages > 1:
                    # 最後のページを除いたWriterを作成
                    final_writer = PdfWriter()
                    for i in range(current_pages - 1):
                        final_writer.add_page(reader.pages[page_num - current_pages + 1 + i])

                    # 最後のページを次のパートの最初のページとして保持
                    next_page = reader.pages[page_num]
                    page_num -= 1  # 現在のページを次回処理するため
                else:
                    # 最後のページまたは単一ページの場合はそのまま保存
                    final_writer = current_writer
                    next_page = None

                # ファイルを保存
                output_path = os.path.join(output_dir, f"{base_name}_part{part_num:02d}.pdf")
                with open(output_path, 'wb') as output_file:
                    final_writer.write(output_file)

                final_size = get_file_size_mb(output_path)
                print(f"Part {part_num}: {current_pages}ページ, {final_size:.2f}MB -> {output_path}")
                output_files.append(output_path)

                # 次のパートの準備
                part_num += 1
                current_writer = PdfWriter()
                current_pages = 0

                # 次のページがある場合は追加
                if next_page is not None:
                    current_writer.add_page(next_page)
                    current_pages = 1

    print(f"分割完了: {len(output_files)}個のファイルを作成")
    return output_files


def main():
    parser = argparse.ArgumentParser(
        description='PDFを指定サイズ以下に分割するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python pdf_split.py -i input.pdf                    # 30MB以下に分割
  python pdf_split.py -i input.pdf -s 50              # 50MB以下に分割
  python pdf_split.py -i input.pdf -o /output/dir     # 出力ディレクトリ指定
        """
    )

    parser.add_argument('-i', '--input', required=True,
                       help='入力PDFファイルのパス')
    parser.add_argument('-s', '--size', type=float, default=25.0,
                       help='最大ファイルサイズ（MB、デフォルト: 30）')
    parser.add_argument('-o', '--output',
                       help='出力ディレクトリ（省略時は入力ファイルと同じディレクトリ）')

    args = parser.parse_args()

    try:
        output_files = split_pdf_by_size(
            args.input,
            max_size_mb=args.size,
            output_dir=args.output
        )

        print("\n=== 分割結果 ===")
        for i, file_path in enumerate(output_files, 1):
            size_mb = get_file_size_mb(file_path)
            print(f"{i}. {os.path.basename(file_path)} ({size_mb:.2f}MB)")

    except Exception as e:
        print(f"エラー: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())

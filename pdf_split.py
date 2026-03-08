import os
import argparse
import tempfile
from PyPDF2 import PdfReader, PdfWriter


def get_file_size_mb(filepath: str) -> float:
    """ファイルサイズをMB単位で取得"""
    return os.path.getsize(filepath) / (1024 * 1024)


def split_pdf_by_size(
    input_pdf_path: str,
    max_size_mb: float = 25,
    output_dir: str | None = None,
) -> list[str]:
    """PDFをファイルサイズ制限で分割する

    Args:
        input_pdf_path: 入力PDFファイルのパス
        max_size_mb: 最大ファイルサイズ（MB）デフォルト25MB
        output_dir: 出力ディレクトリ（Noneの場合は入力ファイルと同じディレクトリ）

    Returns:
        分割されたPDFファイルのパスのリスト
    """
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_pdf_path}")

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_pdf_path))

    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]

    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    print(f"入力PDF: {input_pdf_path}")
    print(f"総ページ数: {total_pages}")
    print(f"元ファイルサイズ: {get_file_size_mb(input_pdf_path):.2f}MB")
    print(f"分割サイズ制限: {max_size_mb}MB")

    output_files: list[str] = []
    part_num = 1
    page_idx = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        while page_idx < total_pages:
            current_writer = PdfWriter()
            part_start = page_idx
            final_writer = current_writer
            pages_count = 0

            while page_idx < total_pages:
                current_writer.add_page(reader.pages[page_idx])
                pages_in_part = page_idx - part_start + 1

                temp_path = os.path.join(temp_dir, f"temp_part_{part_num}.pdf")
                with open(temp_path, 'wb') as f:
                    current_writer.write(f)
                temp_size_mb = get_file_size_mb(temp_path)

                is_last_page = (page_idx == total_pages - 1)
                exceeded = temp_size_mb >= max_size_mb

                if exceeded and pages_in_part > 1:
                    # このページを除いた分を現パートとして確定。このページは次パートの先頭へ。
                    final_writer = PdfWriter()
                    for i in range(part_start, page_idx):
                        final_writer.add_page(reader.pages[i])
                    pages_count = page_idx - part_start
                    # page_idx はインクリメントしない（次パートの先頭として再処理）
                    break
                elif exceeded or is_last_page:
                    # 1ページで制限超過、または最後のページ → このページを含めて保存
                    final_writer = current_writer
                    pages_count = pages_in_part
                    page_idx += 1
                    break
                else:
                    page_idx += 1

            if pages_count == 0:
                break  # 安全ガード（正常系では到達しない）

            output_path = os.path.join(output_dir, f"{base_name}_part{part_num:02d}.pdf")
            with open(output_path, 'wb') as f:
                final_writer.write(f)

            final_size = get_file_size_mb(output_path)
            print(f"Part {part_num}: {pages_count}ページ, {final_size:.2f}MB -> {output_path}")
            output_files.append(output_path)
            part_num += 1

    print(f"分割完了: {len(output_files)}個のファイルを作成")
    return output_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description='PDFを指定サイズ以下に分割するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python pdf_split.py -i input.pdf                    # 25MB以下に分割
  python pdf_split.py -i input.pdf -s 50              # 50MB以下に分割
  python pdf_split.py -i input.pdf -o /output/dir     # 出力ディレクトリ指定
        """
    )

    parser.add_argument('-i', '--input', required=True,
                        help='入力PDFファイルのパス')
    parser.add_argument('-s', '--size', type=float, default=25.0,
                        help='最大ファイルサイズ（MB、デフォルト: 25）')
    parser.add_argument('-o', '--output',
                        help='出力ディレクトリ（省略時は入力ファイルと同じディレクトリ）')

    args = parser.parse_args()

    try:
        output_files = split_pdf_by_size(
            args.input,
            max_size_mb=args.size,
            output_dir=args.output,
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

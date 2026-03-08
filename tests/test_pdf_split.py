import os
import pytest
from PyPDF2 import PdfReader
from pdf_split import get_file_size_mb, split_pdf_by_size


class TestGetFileSizeMb:
    def test_returns_float(self, tmp_path):
        f = tmp_path / "sample.txt"
        f.write_bytes(b"x" * 1024)  # 1KB
        result = get_file_size_mb(str(f))
        assert isinstance(result, float)
        assert abs(result - 1 / 1024) < 0.0001


class TestSplitPdfBySize:
    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            split_pdf_by_size(str(tmp_path / "nonexistent.pdf"))

    def test_single_part_when_small(self, tmp_pdf, tmp_path):
        """PDFがサイズ制限に収まる場合は1ファイルに出力される"""
        input_path = tmp_pdf(num_pages=3)
        output_dir = str(tmp_path / "out")
        os.makedirs(output_dir)

        result = split_pdf_by_size(input_path, max_size_mb=100, output_dir=output_dir)

        assert len(result) == 1
        assert os.path.exists(result[0])

    def test_total_page_count_preserved(self, tmp_pdf, tmp_path):
        """分割後の全ページ数が元PDFと一致する"""
        num_pages = 10
        input_path = tmp_pdf(num_pages=num_pages)
        output_dir = str(tmp_path / "out")
        os.makedirs(output_dir)

        # 必ず分割されるようにサイズ制限を極小に設定
        result = split_pdf_by_size(input_path, max_size_mb=0.001, output_dir=output_dir)

        total_output_pages = sum(len(PdfReader(f).pages) for f in result)
        assert total_output_pages == num_pages

    def test_splits_one_page_per_part_at_zero_size(self, tmp_pdf, tmp_path):
        """max_size_mb=0 のとき1ページごとに分割される"""
        num_pages = 4
        input_path = tmp_pdf(num_pages=num_pages)
        output_dir = str(tmp_path / "out")
        os.makedirs(output_dir)

        result = split_pdf_by_size(input_path, max_size_mb=0, output_dir=output_dir)

        assert len(result) == num_pages
        for path in result:
            assert os.path.exists(path)
            assert len(PdfReader(path).pages) == 1

    def test_output_dir_defaults_to_input_dir(self, tmp_pdf):
        """output_dir=None のとき入力ファイルと同じディレクトリに出力される"""
        input_path = tmp_pdf(num_pages=1)
        input_dir = os.path.dirname(input_path)

        result = split_pdf_by_size(input_path, max_size_mb=100, output_dir=None)

        assert len(result) == 1
        assert os.path.dirname(result[0]) == input_dir

    def test_output_files_named_with_part_number(self, tmp_pdf, tmp_path):
        """出力ファイル名に _part01, _part02 ... が付く"""
        input_path = tmp_pdf(num_pages=3, filename="mybook.pdf")
        output_dir = str(tmp_path / "out")
        os.makedirs(output_dir)

        result = split_pdf_by_size(input_path, max_size_mb=0.001, output_dir=output_dir)

        for i, path in enumerate(result, 1):
            assert f"_part{i:02d}" in os.path.basename(path)

    def test_single_page_exceeding_limit_is_saved_anyway(self, tmp_pdf, tmp_path):
        """1ページしかなくてサイズ制限超過でも、そのまま1ファイルとして保存される"""
        input_path = tmp_pdf(num_pages=1)
        output_dir = str(tmp_path / "out")
        os.makedirs(output_dir)

        # max_size_mb=0 → 1ページでもサイズ超過とみなされる
        result = split_pdf_by_size(input_path, max_size_mb=0, output_dir=output_dir)

        assert len(result) == 1
        assert len(PdfReader(result[0]).pages) == 1

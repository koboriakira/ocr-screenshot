import os
import glob
import pytest
from unittest.mock import patch, MagicMock
from ocr_merge import find_image_files, image_to_pdf_with_ocr, merge_pdfs


class TestFindImageFiles:
    def test_returns_jpg_and_png(self, tmp_path):
        (tmp_path / "a.jpg").write_bytes(b"")
        (tmp_path / "b.jpeg").write_bytes(b"")
        (tmp_path / "c.png").write_bytes(b"")
        (tmp_path / "d.txt").write_bytes(b"")

        result = find_image_files(str(tmp_path))

        basenames = [os.path.basename(f) for f in result]
        assert "a.jpg" in basenames
        assert "b.jpeg" in basenames
        assert "c.png" in basenames
        assert "d.txt" not in basenames

    def test_returns_sorted_order(self, tmp_path):
        for name in ("p003.png", "p001.jpg", "p002.png"):
            (tmp_path / name).write_bytes(b"")

        result = find_image_files(str(tmp_path))

        basenames = [os.path.basename(f) for f in result]
        assert basenames == sorted(basenames)

    def test_empty_directory_returns_empty_list(self, tmp_path):
        result = find_image_files(str(tmp_path))
        assert result == []

    def test_ignores_subdirectories(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "img.png").write_bytes(b"")

        result = find_image_files(str(tmp_path))

        assert result == []


class TestImageToPdfWithOcr:
    def test_writes_pdf_file(self, tmp_path):
        img_path = str(tmp_path / "test.jpg")
        pdf_path = str(tmp_path / "out.pdf")

        fake_pdf_bytes = b"%PDF-1.4 fake content"

        with patch("ocr_merge.Image") as mock_pil, \
             patch("ocr_merge.pytesseract.image_to_pdf_or_hocr", return_value=fake_pdf_bytes):
            mock_pil.open.return_value = MagicMock()
            image_to_pdf_with_ocr(img_path, pdf_path)

        assert os.path.exists(pdf_path)
        assert open(pdf_path, "rb").read() == fake_pdf_bytes

    def test_uses_default_lang(self, tmp_path):
        img_path = str(tmp_path / "test.jpg")
        pdf_path = str(tmp_path / "out.pdf")

        with patch("ocr_merge.Image") as mock_pil, \
             patch("ocr_merge.pytesseract.image_to_pdf_or_hocr", return_value=b"") as mock_ocr:
            mock_pil.open.return_value = MagicMock()
            image_to_pdf_with_ocr(img_path, pdf_path)

        _, kwargs = mock_ocr.call_args
        assert kwargs.get("lang") == "jpn+eng"


class TestMergePdfs:
    def test_merges_multiple_pdfs(self, tmp_path):
        import io
        from PyPDF2 import PdfWriter, PdfReader

        def make_pdf(n_pages: int) -> str:
            writer = PdfWriter()
            for _ in range(n_pages):
                writer.add_blank_page(width=612, height=792)
            buf = io.BytesIO()
            writer.write(buf)
            path = tmp_path / f"part_{n_pages}.pdf"
            path.write_bytes(buf.getvalue())
            return str(path)

        pdf1 = make_pdf(2)
        pdf2 = make_pdf(3)
        output = str(tmp_path / "merged.pdf")

        merge_pdfs([pdf1, pdf2], output)

        reader = PdfReader(output)
        assert len(reader.pages) == 5

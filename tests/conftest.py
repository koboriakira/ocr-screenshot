import os
import io
import pytest
from PyPDF2 import PdfWriter


def _make_pdf_bytes(num_pages: int = 1) -> bytes:
    """テスト用の最小限PDFをバイト列で生成する"""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def tmp_pdf(tmp_path):
    """1ページの一時PDFファイルを返すフィクスチャ"""
    def _make(num_pages: int = 1, filename: str = "test.pdf") -> str:
        path = tmp_path / filename
        path.write_bytes(_make_pdf_bytes(num_pages))
        return str(path)
    return _make

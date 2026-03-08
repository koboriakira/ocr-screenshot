#!/usr/bin/env python3
"""
OCR比較ツール: pytesseract と ndlocr-lite の結果を並べて表示する
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
import pytesseract


def run_tesseract(image_path: Path) -> str:
    try:
        return pytesseract.image_to_string(Image.open(image_path), lang='jpn+eng')
    except Exception as e:
        return f"[Error] {e}"


def run_ndlocr(image_path: Path, ndlocr_src: Path) -> str | None:
    ndlocr_src = ndlocr_src.resolve()
    if not ndlocr_src.exists():
        return None

    ocr_script = ndlocr_src / "ocr.py"
    if not ocr_script.exists():
        return None

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            result = subprocess.run(
                [sys.executable, str(ocr_script), "--sourceimg", str(image_path.resolve()), "--output", tmp_dir],
                cwd=str(ndlocr_src),
                capture_output=True,
                text=True,
                timeout=120,
            )
            stem = image_path.stem
            txt_file = Path(tmp_dir) / f"{stem}.txt"
            if txt_file.exists():
                return txt_file.read_text(encoding="utf-8")
            # ndlocr-liteの出力先がサブディレクトリになる場合を考慮
            for f in Path(tmp_dir).rglob("*.txt"):
                return f.read_text(encoding="utf-8")
            return f"[Error] 出力ファイルが見つかりませんでした\nstdout: {result.stdout}\nstderr: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "[Error] タイムアウト"
        except Exception as e:
            return f"[Error] {e}"


def compare_image(image_path: Path, ndlocr_src: Path | None, output_lines: list[str]) -> None:
    print(f"\n=== {image_path.name} ===")
    output_lines.append(f"<h2>{image_path.name}</h2>")

    # Tesseract
    tesseract_text = run_tesseract(image_path)
    print("\n--- Tesseract (jpn+eng) ---")
    print(tesseract_text)

    # ndlocr-lite
    ndlocr_text = None
    if ndlocr_src is not None:
        ndlocr_text = run_ndlocr(image_path, ndlocr_src)

    print("\n--- ndlocr-lite ---")
    if ndlocr_text is None:
        print("[スキップ] ndlocr-lite が見つかりませんでした")
        ndlocr_text = "(ndlocr-lite not available)"
    else:
        print(ndlocr_text)

    output_lines.append(
        f"<table><tr>"
        f"<th>Tesseract (jpn+eng)</th><th>ndlocr-lite</th>"
        f"</tr><tr>"
        f"<td><pre>{_escape_html(tesseract_text)}</pre></td>"
        f"<td><pre>{_escape_html(ndlocr_text)}</pre></td>"
        f"</tr></table>"
    )


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect_images(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    exts = {".jpg", ".jpeg", ".png"}
    return sorted(p for p in path.iterdir() if p.suffix.lower() in exts)


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR比較ツール: pytesseract vs ndlocr-lite")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--image", help="比較する単一画像ファイル")
    group.add_argument("-d", "--directory", help="画像が入ったディレクトリ（全画像を順次処理）")
    parser.add_argument(
        "--ndlocr-src",
        default=os.environ.get("NDLOCR_LITE_SRC", "./ndlocr-lite/src"),
        help="ndlocr-lite/src のパス (デフォルト: 環境変数 NDLOCR_LITE_SRC または ./ndlocr-lite/src)",
    )
    parser.add_argument("--output", help="HTML出力先ファイルパス（省略時はターミナル出力のみ）")
    args = parser.parse_args()

    ndlocr_src = Path(args.ndlocr_src)
    if not ndlocr_src.exists():
        print(f"[情報] ndlocr-lite が見つかりません ({ndlocr_src})。Tesseractのみ実行します。", file=sys.stderr)
        ndlocr_src = None

    target = Path(args.image) if args.image else Path(args.directory)
    images = collect_images(target)
    if not images:
        print("画像ファイルが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    html_parts: list[str] = []
    for image_path in images:
        compare_image(image_path, ndlocr_src, html_parts)

    if args.output:
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>table{width:100%;border-collapse:collapse}"
            "td,th{border:1px solid #ccc;padding:8px;vertical-align:top;width:50%}"
            "pre{white-space:pre-wrap;word-wrap:break-word}</style></head><body>"
            + "\n".join(html_parts)
            + "</body></html>"
        )
        Path(args.output).write_text(html, encoding="utf-8")
        print(f"\nHTML出力: {args.output}")


if __name__ == "__main__":
    main()

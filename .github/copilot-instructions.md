<!-- @format -->

# ocr-screenshot リポジトリ開発ガイド（Copilot/AI 向け）

## プロジェクト概要

- 画像ファイル（JPEG/PNG 等）を日本語・英語 OCR でテキスト検索可能な PDF に変換し、1 つの PDF ファイルに結合するツール。
- コマンドライン版（ocr_merge.py）と GUI 版（ocr_merge_gui.py, TkEasyGUI 利用）がある。
- Mac/Linux 対応。依存管理は pipenv。

## 主要ファイル

- `ocr_merge.py`: 画像 →OCR 付き PDF 変換＆結合のコア処理。コマンドライン引数で動作。
- `ocr_merge_gui.py`: TkEasyGUI ベースの簡易 GUI。内部で ocr_merge.py をサブプロセス実行。
- `ocr_merge_gui.spec`: PyInstaller 用 spec ファイル。スタンドアロン配布用。
- `README.md`: セットアップ・使い方・配布方法・注意点を記載。

## 依存

- Python 3.13 以上
- pipenv
- pillow, pytesseract, PyPDF2, opencv-python, TkEasyGUI
- Tesseract 本体（brew install tesseract 等で別途インストール必要）

## 開発・運用 Tips

- OCR 処理・PDF 結合は ocr_merge.py に集約。GUI はサブプロセスで呼び出すだけ。
- GUI 配布は PyInstaller で macOS バイナリ化可能（ocr_merge.py も同梱必須）。
- 追加要件（進捗表示・画像リスト・ドラッグ順序・プレビュー等）は未実装。拡張時は GUI 側で TkEasyGUI のフォームやカスタムウィジェットを活用。
- README の手順・注意事項、本マークダウンファイルは常に最新に保つこと。

---

この内容をもとに、AI アシスタントは一貫した設計・運用・ドキュメント更新を心がけてください。

# OCR画像PDF結合ツール

このツールは、指定したディレクトリ内の画像ファイル（JPEG/PNG等）を日本語・英語OCRでテキスト検索可能なPDFに変換し、1つのPDFファイルに結合します。

## 特徴
- 100枚以上の画像にも対応
- 画像ファイル名の昇順で結合
- Mac/Linux対応
- pipenvによる依存管理

## 必要な環境
- Python 3.13以上
- Tesseract OCR（日本語データ含む）
- pipenv

## セットアップ手順

1. **Tesseractのインストール**

### macOSの場合

```sh
brew install tesseract
```

日本語データが必要な場合:
```sh
brew install tesseract-lang
```

または
```sh
brew install tesseract
cd /usr/local/share/tessdata
ls | grep jpn
```

### Linux(Ubuntu)の場合
```sh
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev tesseract-ocr-jpn
```

2. **pipenv環境構築**

```sh
pipenv install
pipenv install pillow pytesseract PyPDF2 opencv-python
```


1. **使い方**

### コマンドライン版

```sh
pipenv run python ocr_merge.py -i 画像ディレクトリ -o 出力PDFファイル名.pdf
```


### GUI版（TkEasyGUI）

#### 1. Pythonスクリプトとして使う場合

依存パッケージをインストール:

```sh
pipenv install TkEasyGUI
```

GUIを起動:

```sh
pipenv run python ocr_merge_gui.py
```

画面の指示に従い「画像ディレクトリ」と「出力PDFファイル名」を指定してください。

※ macOSでtkinterが無い場合は `brew install python-tk` でインストールしてください。

#### 2. スタンドアロン実行ファイルとして使う場合（macOS）

PyInstallerでビルド済みの `dist/ocr_merge_gui` または `dist/ocr_merge_gui.app` を配布・利用できます。

- `ocr_merge_gui` … ターミナルから実行できるバイナリ
- `ocr_merge_gui.app` … Finderからダブルクリックで起動できるアプリ

**注意:**
- `ocr_merge.py` も同じディレクトリにコピーしてください（内部で呼び出します）
- Tesseract本体（`brew install tesseract`）は各自インストールが必要です
- 初回起動時、Gatekeeperの警告が出る場合は「右クリック→開く」で回避できます

自分でビルドする場合は以下のコマンドを実行してください:

```sh
pipenv install pyinstaller
pipenv run pyinstaller --onefile --windowed ocr_merge_gui.py
```

ビルド後、`dist/` フォルダ内に実行ファイルが生成されます。


## オプション（コマンドライン版）
- `-i` : 画像ファイルのディレクトリ
- `-o` : 出力PDFファイル名

## 注意
- Tesseractの日本語OCRパッケージが正しくインストールされていることを確認してください。
- 画像の自動回転補正やエラーハンドリングも実装済みです。
- GUI版はPythonのtkinterが必要です。macOSでエラーが出る場合は `brew install python-tk` でインストールしてください。
- GUIフレームワークはTkEasyGUIを使用しています。

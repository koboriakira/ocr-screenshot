# OCR画像PDF結合・PDF分割ツール

このツールセットは以下の機能を提供します：

1. **OCR画像PDF結合**: 指定したディレクトリ内の画像ファイル（JPEG/PNG等）を日本語・英語OCRでテキスト検索可能なPDFに変換し、1つのPDFファイルに結合
2. **PDF分割**: 任意のPDFファイルを指定したサイズ以下（デフォルト30MB）に分割

## 特徴
- 100枚以上の画像にも対応
- 画像ファイル名の昇順で結合
- PDFサイズベース分割機能
- Mac/Linux対応
- pipenvによる依存管理
- GUI版とコマンドライン版の両方をサポート

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


## 使い方

### 1. OCR画像PDF結合機能

#### コマンドライン版

```sh
pipenv run python ocr_merge.py -i 画像ディレクトリ -o 出力PDFファイル名.pdf
```

#### オプション
- `-i` : 画像ファイルのディレクトリ
- `-o` : 出力PDFファイル名
- `--no-rotate` : 自動回転補正を無効化

### 2. PDF分割機能

#### コマンドライン版

```sh
# 30MB以下に分割（デフォルト）
pipenv run python pdf_split.py -i input.pdf

# 50MB以下に分割
pipenv run python pdf_split.py -i input.pdf -s 50

# 出力ディレクトリを指定
pipenv run python pdf_split.py -i input.pdf -o /path/to/output
```

#### オプション
- `-i` : 入力PDFファイルのパス
- `-s` : 最大ファイルサイズ（MB、デフォルト: 30）
- `-o` : 出力ディレクトリ（省略時は入力ファイルと同じディレクトリ）

### 3. GUI版（TkEasyGUI）

#### 1. Pythonスクリプトとして使う場合

依存パッケージをインストール:

```sh
pipenv install TkEasyGUI
```

##### OCR画像PDF結合のみ
```sh
pipenv run python ocr_merge_gui.py
```

##### 機能選択GUI（OCR結合 or PDF分割）
```sh
pipenv run python pdf_split_gui.py
```

画面の指示に従ってファイル・ディレクトリを選択し、オプションを設定してください。

※ macOSでtkinterが無い場合は `brew install python-tk` でインストールしてください。

#### 2. スタンドアロン実行ファイルとして使う場合（macOS）

PyInstallerで実行ファイルを作成できます。

##### ビルド方法
```sh
pipenv install pyinstaller

# OCR結合GUI
pipenv run pyinstaller --onefile --windowed ocr_merge_gui.py

# 機能選択GUI（OCR結合 + PDF分割）
pipenv run pyinstaller --onefile --windowed pdf_split_gui.py
```

ビルド後、`dist/` フォルダ内に実行ファイルが生成されます。

**注意:**
- OCR機能を使う場合は関連スクリプト（`ocr_merge.py`）も同じディレクトリにコピーしてください
- PDF分割機能を使う場合は `pdf_split.py` も同じディレクトリにコピーしてください
- Tesseract本体（`brew install tesseract`）は各自インストールが必要です（OCR機能使用時）
- 初回起動時、Gatekeeperの警告が出る場合は「右クリック→開く」で回避できます

## 注意事項

### OCR機能について
- Tesseractの日本語OCRパッケージが正しくインストールされていることを確認してください
- 画像の自動回転補正やエラーハンドリングも実装済みです

### PDF分割機能について
- 分割されたファイルは `元ファイル名_part01.pdf`, `元ファイル名_part02.pdf` のような連番で保存されます
- ページ単位での分割のため、1ページが指定サイズを超える場合はそのページだけで1ファイルになります
- PDF分割機能にはTesseractは不要です

### GUI版について
- Pythonのtkinterが必要です。macOSでエラーが出る場合は `brew install python-tk` でインストールしてください
- GUIフレームワークはTkEasyGUIを使用しています

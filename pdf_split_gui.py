import sys
import subprocess
import threading
import TkEasyGUI as eg


def run_pdf_split(cmd, window, output_key):
    try:
        window[output_key].update('', disabled=False)  # 出力欄をクリア
        window[output_key].print('PDF分割処理を開始します...')
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1) as proc:
            while True:
                line = proc.stdout.readline()
                if line:
                    window[output_key].print(line.rstrip())
                elif proc.poll() is not None:
                    break
            # 残りのstderrも表示
            for line in proc.stderr:
                window[output_key].print(f"[ERROR] {line.rstrip()}")
        window[output_key].print('PDF分割処理が完了しました')
    except Exception as e:
        window[output_key].print(f'実行時エラー: {e}')


def main():
    # 機能選択
    choice = eg.popup_yes_no('どちらの機能を使用しますか？',
                            'PDF分割', 'OCR結合',
                            title='機能選択')

    if choice == 'OCR結合':
        # 既存のOCR結合機能を呼び出し
        import ocr_merge_gui
        ocr_merge_gui.main()
        return
    elif choice != 'PDF分割':
        return  # キャンセルされた場合

    # PDF分割用のフォーム入力
    form = eg.popup_get_form([
        ("入力PDFファイル", "", "file"),
        ("出力ディレクトリ", "", "folder"),
        ("最大ファイルサイズ（MB）", "25"),
    ], title="PDF分割ツール")

    if not form:
        return

    input_pdf = form["入力PDFファイル"]
    output_dir = form["出力ディレクトリ"]
    max_size = form["最大ファイルサイズ（MB）"].strip()

    # 入力検証
    if not input_pdf:
        eg.popup_error('入力PDFファイルが選択されていません')
        return
    if not output_dir:
        eg.popup_error('出力ディレクトリが選択されていません')
        return
    if not max_size:
        max_size = "30"

    try:
        max_size_float = float(max_size)
        if max_size_float <= 0:
            eg.popup_error('最大ファイルサイズは正の数値を入力してください')
            return
    except ValueError:
        eg.popup_error('最大ファイルサイズは数値で入力してください')
        return

    # 進捗・エラー表示用ウィンドウ
    layout = [
        [eg.Text('PDF分割 進捗・エラー出力', font=(None, 12))],
        [eg.Multiline('', key='-OUTPUT-', size=(80, 20), autoscroll=True, disabled=True)],
        [eg.Button('閉じる')]
    ]
    window = eg.Window('PDF分割実行ログ', layout)

    cmd = [sys.executable, 'pdf_split.py', '-i', input_pdf, '-o', output_dir, '-s', str(max_size_float)]
    thread = threading.Thread(target=run_pdf_split, args=(cmd, window, '-OUTPUT-'), daemon=True)
    thread.start()

    while True:
        event, _ = window.read(timeout=100)
        if event == '閉じる' or event == eg.WINDOW_CLOSED:
            break
    window.close()


if __name__ == '__main__':
    main()

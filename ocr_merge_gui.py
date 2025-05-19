import sys
import subprocess
import threading
import TkEasyGUI as eg

def run_ocr_merge(cmd, window, output_key):
    try:
        window[output_key].update('', disabled=False)  # 出力欄をクリア
        window[output_key].print('OCR処理を開始します...')
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
        window[output_key].print('全処理が完了しました')
    except Exception as e:
        window[output_key].print(f'実行時エラー: {e}')

def main():
    form = eg.popup_get_form([
        ("画像ディレクトリ", "", "folder"),
        ("出力ディレクトリ", "", "folder"),
        ("出力PDFファイル名（拡張子.pdf省略可）", "output"),
    ], title="OCR画像PDF結合ツール")
    if not form:
        return
    input_dir = form["画像ディレクトリ"]
    output_dir = form["出力ディレクトリ"]
    output_name = form["出力PDFファイル名（拡張子.pdf省略可）"].strip()
    if not input_dir:
        eg.popup_error('画像ディレクトリが選択されていません')
        return
    if not output_dir:
        eg.popup_error('出力ディレクトリが選択されていません')
        return
    if not output_name:
        eg.popup_error('出力PDFファイル名が指定されていません')
        return
    if not output_name.lower().endswith('.pdf'):
        output_name += '.pdf'
    output_pdf = eg.os_path_join(output_dir, output_name) if hasattr(eg, 'os_path_join') else __import__('os').path.join(output_dir, output_name)

    # 進捗・エラー表示用ウィンドウ
    layout = [
        [eg.Text('進捗・エラー出力', font=(None, 12))],
        [eg.Multiline('', key='-OUTPUT-', size=(80, 20), autoscroll=True, disabled=True)],
        [eg.Button('閉じる')]
    ]
    window = eg.Window('OCR実行ログ', layout)

    cmd = [sys.executable, 'ocr_merge.py', '-i', input_dir, '-o', output_pdf]
    thread = threading.Thread(target=run_ocr_merge, args=(cmd, window, '-OUTPUT-'), daemon=True)
    thread.start()

    while True:
        event, _ = window.read(timeout=100)
        if event == '閉じる' or event == eg.WINDOW_CLOSED:
            break
    window.close()

if __name__ == '__main__':
    main()

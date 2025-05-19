
import sys
import subprocess
import TkEasyGUI as eg

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
    eg.popup(f'画像ディレクトリ: {input_dir}\n出力PDF: {output_pdf}', title="確認")
    cmd = [sys.executable, 'ocr_merge.py', '-i', input_dir, '-o', output_pdf]
    eg.popup(f'実行: {cmd}', title="実行コマンド")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            eg.popup(result.stdout, title="標準出力")
        if result.stderr:
            eg.popup_error(result.stderr)
    except Exception as e:
        eg.popup_error(f'実行時エラー: {e}')
    else:
        eg.popup('完了しました', title="完了")

if __name__ == '__main__':
    main()

"""PDF 名前付け直しプログラム

Usage:
    Filename-Associator generate
    Filename-Associator rename

Options:
    -h --help     Show this screen.
"""
import pathlib
import sys

from docopt import docopt
import pandas as pd
import PySimpleGUI as sg

GENERATE_FILE_NAME = "Mustn't_edit_generated_by_programed.xlsx"
BEFORE_NAME = "元の名前"
AFTER_NAME = "後の名前"


def select_dirpath_by_gui():
    layout = [
        [sg.Text("PDF が入ったディレクトリを選択してください。")],
        [sg.Text("ディレクトリ"), sg.InputText(), sg.FolderBrowse(key="dirname")],
        [sg.Submit("OK"), sg.Cancel("終了")],
    ]

    window = sg.Window("ディレクトリ選択", layout)
    _, values = window.read()
    window.close()

    if not values["dirname"]:
        sys.exit(1)

    return values["dirname"]


def show_after_dialog(path):
    layout = [
        [sg.Text(f"""
            {path.resolve()}
            にエクセルファイルが生成されました。
            対応表を完成させ、filename-associator rename を実行してください.
            元の名前はハイパーリンクになっており、クリックすると対象のファイルが開きます.
        """)],
        [sg.Submit("確認しました.")],
    ]

    window = sg.Window("確認 ダイアログ", layout)
    window.read()
    window.close()


def generate():
    dir_path = pathlib.Path(select_dirpath_by_gui())
    try:
        origin_filenames = dir_path.glob("*")
    except Exception:
        print(f"該当するディレクトリが存在しません: {dir_path}")

    df = pd.DataFrame()
    df[BEFORE_NAME] = [
        f"=HYPERLINK(\"{str(file_path.resolve())}\", \"{file_path.name}\")"
        for file_path in origin_filenames
    ]
    df[AFTER_NAME] = ""

    df.to_excel(dir_path / GENERATE_FILE_NAME, index=False)
    show_after_dialog(dir_path / GENERATE_FILE_NAME)


def rename():
    dir_path = pathlib.Path(select_dirpath_by_gui())

    try:
        df = pd.read_excel(str(dir_path / GENERATE_FILE_NAME))
    # XXX: 読み込みエラー以外のエラーも見つからないで済んでしまう。
    except Exception:
        print(
            "対応表が見つかりません. filename-associator generate"
            "を実行し、生成してから再度実行してください。"
        )

    for _, rows in df.iterrows():
        (dir_path / rows[BEFORE_NAME]).rename(dir_path / rows[AFTER_NAME])


def main():
    args = docopt(__doc__)
    if args["generate"]:
        generate()
    elif args["rename"]:
        rename()


if __name__ == "__main__":
    main()

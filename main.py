import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from ui.styles import STYLESHEET


XLSX_FILENAME = "english-wordbook.xlsx"


def find_xlsx() -> Path:
    """앱과 같은 폴더에서 xlsx를 찾아 반환. 없으면 새 파일 경로 반환."""
    default = Path(__file__).parent / XLSX_FILENAME
    return default


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("영어 단어장")

    xlsx_path = find_xlsx()
    window = MainWindow(xlsx_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

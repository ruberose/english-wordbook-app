import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import STYLESHEET
import config


def _seed_path() -> Path:
    """번들(PyInstaller) 또는 개발 환경의 seed xlsx 경로."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / config.XLSX_FILENAME
    return Path(__file__).parent / config.XLSX_FILENAME


def get_xlsx_path() -> Path:
    """실제 사용할 xlsx 경로.

    우선순위:
    1. 사용자가 직접 지정한 경로 (config.json)
    2. AppData 기본 경로 (없으면 seed 파일로 초기화)
    """
    path = config.load_xlsx_path()
    if not path.exists():
        seed = _seed_path()
        if seed.exists():
            shutil.copy(seed, path)
    return path


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("영어 단어장")

    xlsx_path = get_xlsx_path()
    window = MainWindow(xlsx_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

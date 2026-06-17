from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel,
    QMenuBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from data.repository import WordbookRepository
from ui.add_tab import AddTab
from ui.review_tab import ReviewTab
from ui.quiz_tab import QuizTab
from ui.stats_tab import StatsTab
from ui.wordlist_tab import WordlistTab
import config


class MainWindow(QMainWindow):
    def __init__(self, xlsx_path: Path):
        super().__init__()
        self._xlsx_path = xlsx_path
        self._repo = WordbookRepository(xlsx_path)

        self.setWindowTitle("영어 단어장")
        self.setMinimumSize(900, 620)
        self._set_icon()
        self._build_ui()
        self._refresh_all()

    def _set_icon(self):
        import sys
        if hasattr(sys, "_MEIPASS"):
            icon_path = Path(sys._MEIPASS) / "assets" / "icon.ico"
        else:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _build_ui(self):
        # 메뉴바
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일")

        change_path_action = QAction("단어장 파일 위치 변경...", self)
        change_path_action.triggered.connect(self._on_change_path)
        file_menu.addAction(change_path_action)

        open_folder_action = QAction("단어장 파일 폴더 열기", self)
        open_folder_action.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_folder_action)

        # 탭
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        self._add_tab = AddTab(self._repo)
        self._review_tab = ReviewTab(self._repo)
        self._quiz_tab = QuizTab(self._repo)
        self._stats_tab = StatsTab(self._repo)
        self._wordlist_tab = WordlistTab(self._repo)

        tabs.addTab(self._add_tab, "📝  단어 추가")
        tabs.addTab(self._review_tab, "📅  오늘의 복습")
        tabs.addTab(self._quiz_tab, "🎯  퀴즈")
        tabs.addTab(self._stats_tab, "📊  통계")
        tabs.addTab(self._wordlist_tab, "📚  단어 목록")

        self.setCentralWidget(tabs)

        # 상태바
        self._status = QStatusBar()
        self._status_label = QLabel()
        self._status.addWidget(self._status_label)
        self.setStatusBar(self._status)

        # 시그널 연결
        self._add_tab.word_added.connect(self._on_data_changed)
        self._review_tab.entries_updated.connect(self._on_data_changed)
        self._quiz_tab.entries_updated.connect(self._on_data_changed)
        self._wordlist_tab.entries_updated.connect(self._on_data_changed)

    def _refresh_all(self):
        entries = self._repo.load_all()
        self._review_tab.refresh(entries)
        self._quiz_tab.refresh(entries)
        self._stats_tab.refresh(entries)
        self._wordlist_tab.refresh(entries)
        self._status_label.setText(f"단어 {len(entries)}개  |  📂 {self._repo.path}")

    def _on_data_changed(self, *args):
        self._refresh_all()

    def _on_change_path(self):
        """사용자가 새 xlsx 경로를 직접 선택."""
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "단어장 파일 위치 선택",
            str(self._xlsx_path.parent),
            "Excel 파일 (*.xlsx)",
        )
        if not new_path:
            return

        new_path = Path(new_path)
        if not new_path.suffix:
            new_path = new_path.with_suffix(".xlsx")

        # 기존 파일이 없는 새 경로면 현재 데이터 복사
        if not new_path.exists():
            import shutil
            shutil.copy(self._xlsx_path, new_path)

        config.save_xlsx_path(new_path)
        self._xlsx_path = new_path
        self._repo = WordbookRepository(new_path)

        # 모든 탭의 repo 교체
        self._add_tab._repo = self._repo
        self._review_tab._repo = self._repo
        self._quiz_tab._repo = self._repo
        self._wordlist_tab._repo = self._repo

        self._refresh_all()
        QMessageBox.information(
            self, "경로 변경 완료",
            f"단어장 파일이 다음 위치로 변경되었습니다:\n{new_path}\n\n"
            "OneDrive/Google Drive 폴더를 선택하면\n다른 컴퓨터와 자동으로 동기화됩니다."
        )

    def _on_open_folder(self):
        """탐색기에서 단어장 파일 폴더 열기."""
        import subprocess
        subprocess.Popen(f'explorer /select,"{self._xlsx_path}"')

    def _on_tab_changed(self, index: int):
        pass

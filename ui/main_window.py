from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel
from PyQt6.QtCore import Qt

from data.repository import WordbookRepository
from ui.add_tab import AddTab
from ui.review_tab import ReviewTab
from ui.quiz_tab import QuizTab
from ui.stats_tab import StatsTab
from ui.wordlist_tab import WordlistTab


class MainWindow(QMainWindow):
    def __init__(self, xlsx_path: Path):
        super().__init__()
        self._repo = WordbookRepository(xlsx_path)
        self._entries = self._repo.load_all()

        self.setWindowTitle("영어 단어장")
        self.setMinimumSize(900, 620)
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
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

        tabs.currentChanged.connect(self._on_tab_changed)

    def _refresh_all(self):
        self._entries = self._repo.load_all()
        self._review_tab.refresh(self._entries)
        self._quiz_tab.refresh(self._entries)
        self._stats_tab.refresh(self._entries)
        self._wordlist_tab.refresh(self._entries)
        self._status_label.setText(f"단어 {len(self._entries)}개 로드됨  |  {self._repo.path}")

    def _on_data_changed(self, *args):
        self._refresh_all()

    def _on_tab_changed(self, index: int):
        pass

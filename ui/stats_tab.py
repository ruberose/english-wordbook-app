from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt

from data.models import WordEntry


class StatsTab(QWidget):
    def __init__(self, repo):
        super().__init__()
        self._repo = repo
        self._all_entries: list[WordEntry] = []
        self._build_ui()

    def refresh(self, all_entries: list[WordEntry]):
        self._all_entries = all_entries
        self._update_stats()
        self._update_table(all_entries)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("통계 & 단어 목록")
        title.setStyleSheet("font-size:17px; font-weight:700;")
        layout.addWidget(title)

        # 통계 카드 행
        stats_row = QHBoxLayout()
        self._stat_total = self._make_stat_card("전체 단어", "0")
        self._stat_due = self._make_stat_card("오늘 복습", "0")
        self._stat_early = self._make_stat_card("초기", "0")
        self._stat_mid = self._make_stat_card("중기", "0")
        self._stat_long = self._make_stat_card("장기", "0")
        for card in [self._stat_total, self._stat_due, self._stat_early, self._stat_mid, self._stat_long]:
            stats_row.addWidget(card)
        layout.addLayout(stats_row)

        # 검색 & 필터
        filter_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("단어 검색...")
        self._search.textChanged.connect(self._on_filter)
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("전체", "all")
        self._filter_combo.addItem("복습 필요", "review")
        for key, label in WordEntry.WORD_TYPES.items():
            self._filter_combo.addItem(label, key)
        for lbl in WordEntry.LABELS:
            self._filter_combo.addItem(f"단계: {lbl}", f"label_{lbl}")
        self._filter_combo.currentIndexChanged.connect(self._on_filter)
        filter_row.addWidget(self._search, 2)
        filter_row.addWidget(self._filter_combo, 1)
        layout.addLayout(filter_row)

        # 단어 테이블
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["단어", "뜻", "유형", "단계", "복습 횟수", "다음 복습일"])
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def _make_stat_card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("stat_card")
        card.setStyleSheet("QFrame#stat_card { background:#fff; border:1px solid #dee2e6; border-radius:10px; }")
        card.setMinimumWidth(90)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 12, 12, 12)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        num = QLabel(value)
        num.setObjectName("stat_number")
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet("font-size:24px; font-weight:700; color:#4361ee;")

        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:11px; color:#868e96;")

        cl.addWidget(num)
        cl.addWidget(lbl)
        card._num_label = num
        return card

    def _update_stats(self):
        entries = self._all_entries
        today = date.today()
        due = sum(1 for e in entries if e.next_review <= today)
        early = sum(1 for e in entries if e.label == "초기")
        mid = sum(1 for e in entries if e.label == "중기")
        long_ = sum(1 for e in entries if e.label == "장기")

        self._stat_total._num_label.setText(str(len(entries)))
        self._stat_due._num_label.setText(str(due))
        self._stat_early._num_label.setText(str(early))
        self._stat_mid._num_label.setText(str(mid))
        self._stat_long._num_label.setText(str(long_))

    def _update_table(self, entries: list[WordEntry]):
        self._table.setRowCount(0)
        for entry in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(entry.word))
            self._table.setItem(row, 1, QTableWidgetItem(entry.meaning))
            self._table.setItem(row, 2, QTableWidgetItem(entry.type_display()))
            self._table.setItem(row, 3, QTableWidgetItem(entry.label))
            self._table.setItem(row, 4, QTableWidgetItem(str(entry.review_count)))
            self._table.setItem(row, 5, QTableWidgetItem(str(entry.next_review)))

    def _on_filter(self):
        keyword = self._search.text().strip().lower()
        scope = self._filter_combo.currentData()
        today = date.today()

        filtered = []
        for e in self._all_entries:
            if keyword and keyword not in e.word.lower() and keyword not in e.meaning.lower():
                continue
            if scope == "review" and e.next_review > today:
                continue
            if scope in WordEntry.WORD_TYPES and e.word_type != scope:
                continue
            if scope.startswith("label_") and e.label != scope[6:]:
                continue
            filtered.append(e)
        self._update_table(filtered)

"""단어 목록 전용 탭 — 편집/삭제 지원."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QDialog, QFormLayout, QTextEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import WordEntry


class WordlistTab(QWidget):
    entries_updated = pyqtSignal()

    def __init__(self, repo):
        super().__init__()
        self._repo = repo
        self._all_entries: list[WordEntry] = []
        self._build_ui()

    def refresh(self, all_entries: list[WordEntry]):
        self._all_entries = all_entries
        self._apply_filter()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("단어 목록")
        title.setStyleSheet("font-size:17px; font-weight:700;")
        layout.addWidget(title)

        # 검색 & 필터
        filter_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("단어 검색...")
        self._search.textChanged.connect(self._apply_filter)
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("전체", "all")
        for key, label in WordEntry.WORD_TYPES.items():
            self._filter_combo.addItem(label, key)
        for lbl in WordEntry.LABELS:
            self._filter_combo.addItem(f"단계: {lbl}", f"label_{lbl}")
        self._filter_combo.currentIndexChanged.connect(self._apply_filter)
        filter_row.addWidget(self._search, 2)
        filter_row.addWidget(self._filter_combo, 1)
        layout.addLayout(filter_row)

        # 테이블
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["단어", "뜻", "유형", "단계", "기억강도", "다음 복습일"])
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self._table)

        # 하단 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        edit_btn = QPushButton("편집")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self._on_edit)
        del_btn = QPushButton("삭제")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

    def _apply_filter(self):
        keyword = self._search.text().strip().lower()
        scope = self._filter_combo.currentData()
        filtered = []
        for e in self._all_entries:
            if keyword and keyword not in e.word.lower() and keyword not in e.meaning.lower():
                continue
            if scope in WordEntry.WORD_TYPES and e.word_type != scope:
                continue
            if scope.startswith("label_") and e.label != scope[6:]:
                continue
            filtered.append(e)
        self._render(filtered)
        self._displayed = filtered

    def _render(self, entries: list[WordEntry]):
        self._table.setRowCount(0)
        for entry in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(entry.word))
            self._table.setItem(row, 1, QTableWidgetItem(entry.meaning))
            self._table.setItem(row, 2, QTableWidgetItem(entry.type_display()))
            self._table.setItem(row, 3, QTableWidgetItem(entry.label))
            self._table.setItem(row, 4, QTableWidgetItem(str(entry.memory_strength)))
            self._table.setItem(row, 5, QTableWidgetItem(str(entry.next_review)))

    def _selected_entry(self) -> WordEntry | None:
        rows = self._table.selectedItems()
        if not rows:
            return None
        row = self._table.currentRow()
        if row >= len(self._displayed):
            return None
        return self._displayed[row]

    def _on_edit(self):
        entry = self._selected_entry()
        if not entry:
            return
        dlg = EditDialog(entry, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_entry()
            self._repo.update(updated)
            self.entries_updated.emit()

    def _on_delete(self):
        entry = self._selected_entry()
        if not entry:
            return
        reply = QMessageBox.question(
            self, "삭제 확인", f"'{entry.word}' 단어를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._repo.delete(entry)
            self.entries_updated.emit()


class EditDialog(QDialog):
    def __init__(self, entry: WordEntry, parent=None):
        super().__init__(parent)
        self._entry = entry
        self.setWindowTitle("단어 편집")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self._type_combo = QComboBox()
        for key, label in WordEntry.WORD_TYPES.items():
            self._type_combo.addItem(label, key)
        self._type_combo.setCurrentIndex(
            list(WordEntry.WORD_TYPES.keys()).index(self._entry.word_type)
        )
        form.addRow("유형", self._type_combo)

        self._word_edit = QLineEdit(self._entry.word)
        form.addRow("영어 표현", self._word_edit)

        self._meaning_edit = QLineEdit(self._entry.meaning)
        form.addRow("한국어 뜻", self._meaning_edit)

        self._example_edit = QTextEdit(self._entry.example)
        self._example_edit.setMaximumHeight(70)
        form.addRow("예문", self._example_edit)

        self._trans_edit = QTextEdit(self._entry.example_translation)
        self._trans_edit.setMaximumHeight(70)
        form.addRow("예문 번역", self._trans_edit)

        layout.addLayout(form)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_entry(self) -> WordEntry:
        from dataclasses import replace
        return replace(
            self._entry,
            word_type=self._type_combo.currentData(),
            word=self._word_edit.text().strip(),
            meaning=self._meaning_edit.text().strip(),
            example=self._example_edit.toPlainText().strip(),
            example_translation=self._trans_edit.toPlainText().strip(),
        )

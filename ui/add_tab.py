from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import WordEntry


class AddTab(QWidget):
    word_added = pyqtSignal(WordEntry)

    def __init__(self, repo):
        super().__init__()
        self._repo = repo
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        title = QLabel("새 단어 추가")
        title.setStyleSheet("font-size:17px; font-weight:700; margin-bottom:10px;")
        outer.addWidget(title)

        card = QFrame()
        card.setObjectName("card_frame")
        card.setStyleSheet("QFrame#card_frame { background:#fff; border:1px solid #dee2e6; border-radius:12px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(12)

        # 유형
        self._type_combo = QComboBox()
        for key, label in WordEntry.WORD_TYPES.items():
            self._type_combo.addItem(label, key)
        form.addRow("유형", self._type_combo)

        # 단어
        self._word_edit = QLineEdit()
        self._word_edit.setPlaceholderText("영어 단어 또는 표현 입력")
        form.addRow("영어 표현", self._word_edit)

        # 뜻
        self._meaning_edit = QLineEdit()
        self._meaning_edit.setPlaceholderText("한국어 뜻 입력")
        form.addRow("한국어 뜻", self._meaning_edit)

        # 예문
        self._example_edit = QTextEdit()
        self._example_edit.setPlaceholderText("영어 예문 (선택)")
        self._example_edit.setMaximumHeight(70)
        form.addRow("예문", self._example_edit)

        # 예문 번역
        self._trans_edit = QTextEdit()
        self._trans_edit.setPlaceholderText("예문 번역 (선택)")
        self._trans_edit.setMaximumHeight(70)
        form.addRow("예문 번역", self._trans_edit)

        card_layout.addLayout(form)

        # 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._clear_btn = QPushButton("초기화")
        self._clear_btn.setObjectName("secondary")
        self._save_btn = QPushButton("저장")
        self._save_btn.setObjectName("primary")
        self._save_btn.setMinimumWidth(90)
        btn_row.addWidget(self._clear_btn)
        btn_row.addWidget(self._save_btn)
        card_layout.addLayout(btn_row)

        outer.addWidget(card)
        outer.addStretch()

        self._save_btn.clicked.connect(self._on_save)
        self._clear_btn.clicked.connect(self._clear_form)
        self._word_edit.returnPressed.connect(self._meaning_edit.setFocus)

    def _on_save(self):
        word = self._word_edit.text().strip()
        meaning = self._meaning_edit.text().strip()
        if not word or not meaning:
            QMessageBox.warning(self, "입력 오류", "영어 표현과 한국어 뜻은 필수입니다.")
            return

        entry = WordEntry(
            word=word,
            meaning=meaning,
            word_type=self._type_combo.currentData(),
            example=self._example_edit.toPlainText().strip(),
            example_translation=self._trans_edit.toPlainText().strip(),
            added_date=date.today(),
            next_review=date.today(),
        )
        entry = self._repo.add(entry)
        self.word_added.emit(entry)
        self._clear_form()
        QMessageBox.information(self, "저장 완료", f"'{word}' 단어가 저장되었습니다.")

    def _clear_form(self):
        self._word_edit.clear()
        self._meaning_edit.clear()
        self._example_edit.clear()
        self._trans_edit.clear()
        self._word_edit.setFocus()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import WordEntry
from logic.forgetting import get_due_entries, update_after_review


class ReviewTab(QWidget):
    entries_updated = pyqtSignal()

    def __init__(self, repo):
        super().__init__()
        self._repo = repo
        self._queue: list[WordEntry] = []
        self._current: WordEntry | None = None
        self._showing_answer = False
        self._correct = 0
        self._total = 0
        self._build_ui()

    def refresh(self, all_entries: list[WordEntry]):
        self._queue = get_due_entries(all_entries)
        self._correct = 0
        self._total = len(self._queue)
        self._next_card()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("오늘의 복습")
        title.setStyleSheet("font-size:17px; font-weight:700;")
        layout.addWidget(title)

        self._progress_label = QLabel("")
        self._progress_label.setStyleSheet("color:#868e96; font-size:12px;")
        layout.addWidget(self._progress_label)

        # 카드
        self._card = QFrame()
        self._card.setObjectName("card_frame")
        self._card.setMinimumHeight(260)
        card_layout = QVBoxLayout(self._card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(12)

        self._word_label = QLabel("")
        self._word_label.setObjectName("card_word")
        self._word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._word_label.setWordWrap(True)

        self._type_label = QLabel("")
        self._type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._type_label.setStyleSheet("color:#868e96; font-size:12px;")

        self._meaning_label = QLabel("")
        self._meaning_label.setObjectName("card_meaning")
        self._meaning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._meaning_label.setWordWrap(True)

        self._example_label = QLabel("")
        self._example_label.setObjectName("card_example")
        self._example_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._example_label.setWordWrap(True)

        self._hint_label = QLabel("탭하여 뜻 확인")
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint_label.setStyleSheet("color:#adb5bd; font-size:12px; font-style:italic;")

        card_layout.addWidget(self._type_label)
        card_layout.addWidget(self._word_label)
        card_layout.addWidget(self._meaning_label)
        card_layout.addWidget(self._example_label)
        card_layout.addWidget(self._hint_label)
        layout.addWidget(self._card)

        # 버튼
        btn_row = QHBoxLayout()
        self._show_btn = QPushButton("뜻 확인")
        self._show_btn.setObjectName("secondary")
        self._show_btn.setMinimumHeight(44)

        self._wrong_btn = QPushButton("✗  몰랐다")
        self._wrong_btn.setObjectName("danger")
        self._wrong_btn.setMinimumHeight(44)
        self._wrong_btn.hide()

        self._correct_btn = QPushButton("✓  알았다")
        self._correct_btn.setObjectName("success")
        self._correct_btn.setMinimumHeight(44)
        self._correct_btn.hide()

        btn_row.addWidget(self._show_btn)
        btn_row.addWidget(self._wrong_btn)
        btn_row.addWidget(self._correct_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        self._show_btn.clicked.connect(self._reveal_answer)
        self._correct_btn.clicked.connect(lambda: self._submit(True))
        self._wrong_btn.clicked.connect(lambda: self._submit(False))

    def _next_card(self):
        self._showing_answer = False
        if not self._queue:
            self._show_done()
            return
        self._current = self._queue.pop(0)
        remaining = len(self._queue) + 1
        self._progress_label.setText(f"남은 단어: {remaining} / {self._total}")
        self._word_label.setText(self._current.word)
        self._type_label.setText(self._current.type_display())
        self._meaning_label.hide()
        self._example_label.hide()
        self._hint_label.show()
        self._show_btn.show()
        self._wrong_btn.hide()
        self._correct_btn.hide()

    def _reveal_answer(self):
        if self._current is None:
            return
        self._meaning_label.setText(self._current.meaning)
        self._meaning_label.show()
        if self._current.example:
            self._example_label.setText(
                f"{self._current.example}\n{self._current.example_translation}"
            )
            self._example_label.show()
        self._hint_label.hide()
        self._show_btn.hide()
        self._wrong_btn.show()
        self._correct_btn.show()

    def _submit(self, correct: bool):
        if self._current is None:
            return
        if correct:
            self._correct += 1
        updated = update_after_review(self._current, correct)
        self._repo.update(updated)
        self.entries_updated.emit()
        self._next_card()

    def _show_done(self):
        self._word_label.setText("복습 완료!")
        self._type_label.setText("")
        self._meaning_label.hide()
        self._example_label.hide()
        self._hint_label.hide()
        self._show_btn.hide()
        self._wrong_btn.hide()
        self._correct_btn.hide()
        rate = int(self._correct / self._total * 100) if self._total else 0
        self._progress_label.setText(
            f"오늘 복습 완료  |  정답률 {rate}%  ({self._correct}/{self._total})"
        )

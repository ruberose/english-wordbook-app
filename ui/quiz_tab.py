from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QButtonGroup, QRadioButton, QComboBox, QSpinBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

from data.models import WordEntry
from logic.quiz import build_questions, QuizQuestion
from logic.forgetting import update_after_review


class QuizTab(QWidget):
    entries_updated = pyqtSignal()

    def __init__(self, repo):
        super().__init__()
        self._repo = repo
        self._all_entries: list[WordEntry] = []
        self._questions: list[QuizQuestion] = []
        self._current_idx = 0
        self._score = 0
        self._build_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def refresh(self, all_entries: list[WordEntry]):
        self._all_entries = all_entries

    def _build_ui(self):
        self._stack_layout = QVBoxLayout(self)
        self._stack_layout.setContentsMargins(20, 20, 20, 20)

        self._setup_panel = self._build_setup_panel()
        self._quiz_panel = self._build_quiz_panel()
        self._result_panel = self._build_result_panel()

        self._stack_layout.addWidget(self._setup_panel)
        self._stack_layout.addWidget(self._quiz_panel)
        self._stack_layout.addWidget(self._result_panel)

        self._show_panel("setup")

    def _build_setup_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        title = QLabel("퀴즈 설정")
        title.setStyleSheet("font-size:17px; font-weight:700;")
        layout.addWidget(title)

        card = QFrame()
        card.setStyleSheet("background:#fff; border:1px solid #dee2e6; border-radius:12px;")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(14)

        # 출제 범위
        scope_row = QHBoxLayout()
        scope_row.addWidget(QLabel("출제 범위"))
        self._scope_combo = QComboBox()
        self._scope_combo.addItem("전체 단어", "all")
        self._scope_combo.addItem("복습 필요 단어만", "review")
        self._scope_combo.addItem("초기 단계만", "초기")
        self._scope_combo.addItem("중기 단계만", "중기")
        self._scope_combo.addItem("장기 단계만", "장기")
        scope_row.addWidget(self._scope_combo)
        scope_row.addStretch()
        cl.addLayout(scope_row)

        # 문제 수
        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("문제 수"))
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 50)
        self._count_spin.setValue(10)
        count_row.addWidget(self._count_spin)
        count_row.addStretch()
        cl.addLayout(count_row)

        start_btn = QPushButton("퀴즈 시작")
        start_btn.setObjectName("primary")
        start_btn.setMinimumHeight(42)
        start_btn.clicked.connect(self._start_quiz)
        cl.addWidget(start_btn)

        layout.addWidget(card)
        layout.addStretch()
        return w

    def _build_quiz_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)

        self._q_progress = QLabel("")
        self._q_progress.setStyleSheet("color:#868e96; font-size:12px;")
        layout.addWidget(self._q_progress)

        self._q_word = QLabel("")
        self._q_word.setObjectName("card_word")
        self._q_word.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._q_word.setWordWrap(True)
        layout.addWidget(self._q_word)

        self._choice_group = QButtonGroup(self)
        self._choice_btns: list[QPushButton] = []
        for i in range(4):
            btn = QPushButton("")
            btn.setMinimumHeight(46)
            btn.setObjectName("secondary")
            btn.clicked.connect(lambda _, idx=i: self._on_choice(idx))
            self._choice_btns.append(btn)
            layout.addWidget(btn)

        self._feedback_label = QLabel("")
        self._feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feedback_label.setStyleSheet("font-weight:600; font-size:14px;")
        layout.addWidget(self._feedback_label)

        self._next_btn = QPushButton("다음 →  (Enter)")
        self._next_btn.setObjectName("primary")
        self._next_btn.setMinimumHeight(42)
        self._next_btn.hide()
        self._next_btn.clicked.connect(self._next_question)
        layout.addWidget(self._next_btn)

        shortcut_hint = QLabel("키보드: 1 · 2 · 3 · 4 로 선택  /  Enter 로 다음")
        shortcut_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_hint.setStyleSheet("color:#ced4da; font-size:11px; margin-top:4px;")
        layout.addWidget(shortcut_hint)

        layout.addStretch()
        return w

    def _build_result_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self._result_title = QLabel("퀴즈 완료!")
        self._result_title.setStyleSheet("font-size:22px; font-weight:700;")
        self._result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._result_score = QLabel("")
        self._result_score.setObjectName("stat_number")
        self._result_score.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._result_detail = QLabel("")
        self._result_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_detail.setStyleSheet("color:#6c757d;")

        retry_btn = QPushButton("다시 풀기")
        retry_btn.setObjectName("primary")
        retry_btn.clicked.connect(lambda: self._show_panel("setup"))

        layout.addWidget(self._result_title)
        layout.addWidget(self._result_score)
        layout.addWidget(self._result_detail)
        layout.addWidget(retry_btn)
        return w

    # ── 퀴즈 흐름 ────────────────────────────────────────────────────────

    def _start_quiz(self):
        scope = self._scope_combo.currentData()
        if scope == "all":
            pool = self._all_entries
        elif scope == "review":
            pool = [e for e in self._all_entries if e.needs_review]
        else:
            pool = [e for e in self._all_entries if e.label == scope]

        if len(pool) < 2:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "단어 부족", "퀴즈를 위해 최소 2개 이상의 단어가 필요합니다.")
            return

        self._questions = build_questions(pool, self._all_entries, self._count_spin.value())
        self._current_idx = 0
        self._score = 0
        self._show_panel("quiz")
        self._load_question()

    def _load_question(self):
        q = self._questions[self._current_idx]
        total = len(self._questions)
        self._q_progress.setText(f"{self._current_idx + 1} / {total}")
        self._q_word.setText(q.entry.word)
        self._feedback_label.setText("")
        self._next_btn.hide()

        for i, btn in enumerate(self._choice_btns):
            btn.setText(q.choices[i])
            btn.setEnabled(True)
            btn.setStyleSheet("")

    def _on_choice(self, idx: int):
        q = self._questions[self._current_idx]
        correct = idx == q.answer_index

        for i, btn in enumerate(self._choice_btns):
            btn.setEnabled(False)
            if i == q.answer_index:
                btn.setStyleSheet("background:#2dc653; color:white;")
            elif i == idx and not correct:
                btn.setStyleSheet("background:#e63946; color:white;")

        updated = update_after_review(q.entry, correct)
        self._repo.update(updated)
        self.entries_updated.emit()

        if correct:
            self._score += 1
            self._feedback_label.setText("✓ 정답!")
            self._feedback_label.setStyleSheet("color:#2dc653; font-weight:700; font-size:14px;")
        else:
            self._feedback_label.setText(f"✗ 오답  —  정답: {q.entry.meaning}")
            self._feedback_label.setStyleSheet("color:#e63946; font-weight:700; font-size:14px;")

        self._next_btn.show()

    def _next_question(self):
        self._current_idx += 1
        if self._current_idx >= len(self._questions):
            self._show_result()
        else:
            self._load_question()

    def _show_result(self):
        total = len(self._questions)
        rate = int(self._score / total * 100) if total else 0
        self._result_score.setText(f"{rate}%")
        self._result_detail.setText(f"정답 {self._score} / {total}문제")
        self._show_panel("result")

    def _show_panel(self, name: str):
        self._setup_panel.setVisible(name == "setup")
        self._quiz_panel.setVisible(name == "quiz")
        self._result_panel.setVisible(name == "result")

    def keyPressEvent(self, event: QKeyEvent):
        if not self._quiz_panel.isVisible():
            super().keyPressEvent(event)
            return
        key = event.key()
        # 1~4: 보기 선택 (버튼이 활성화된 상태일 때만)
        num_map = {
            Qt.Key.Key_1: 0, Qt.Key.Key_2: 1,
            Qt.Key.Key_3: 2, Qt.Key.Key_4: 3,
        }
        if key in num_map:
            idx = num_map[key]
            if self._choice_btns[idx].isEnabled():
                self._on_choice(idx)
        # Enter/Space: 다음 문제
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if self._next_btn.isVisible():
                self._next_question()
        super().keyPressEvent(event)

"""공통 스타일시트 — 나중에 모바일용 테마로 교체하기 쉽도록 분리."""

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f8f9fa;
    font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #1a1a2e;
}

QTabWidget::pane {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background: #ffffff;
}

QTabBar::tab {
    padding: 10px 20px;
    background: #e9ecef;
    border: 1px solid #dee2e6;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    min-width: 90px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #4361ee;
    border-bottom: 2px solid #4361ee;
}

QTabBar::tab:hover:!selected {
    background: #d0d7de;
}

QPushButton {
    padding: 8px 18px;
    border-radius: 6px;
    border: none;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#primary {
    background-color: #4361ee;
    color: white;
}

QPushButton#primary:hover { background-color: #3451d1; }
QPushButton#primary:pressed { background-color: #2c44b5; }

QPushButton#success {
    background-color: #2dc653;
    color: white;
}

QPushButton#success:hover { background-color: #25a845; }

QPushButton#danger {
    background-color: #e63946;
    color: white;
}

QPushButton#danger:hover { background-color: #c1121f; }

QPushButton#secondary {
    background-color: #e9ecef;
    color: #495057;
    border: 1px solid #ced4da;
}

QPushButton#secondary:hover { background-color: #dee2e6; }

QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 7px 10px;
    background: #ffffff;
    selection-background-color: #4361ee;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #4361ee;
}

QComboBox::drop-down { border: none; width: 24px; }

QTableWidget {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    gridline-color: #f0f0f0;
    background: #ffffff;
    alternate-background-color: #f8f9fa;
}

QTableWidget::item { padding: 6px 8px; }
QTableWidget::item:selected { background: #dde3ff; color: #1a1a2e; }

QHeaderView::section {
    background: #f1f3f5;
    border: none;
    border-right: 1px solid #dee2e6;
    border-bottom: 1px solid #dee2e6;
    padding: 7px 10px;
    font-weight: 600;
    color: #495057;
}

QLabel#card_word {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a2e;
}

QLabel#card_meaning {
    font-size: 20px;
    color: #4361ee;
    font-weight: 600;
}

QLabel#card_example {
    font-size: 13px;
    color: #6c757d;
}

QLabel#stat_number {
    font-size: 28px;
    font-weight: 700;
    color: #4361ee;
}

QLabel#stat_label {
    font-size: 11px;
    color: #868e96;
}

QFrame#card_frame {
    background: #ffffff;
    border: 2px solid #dee2e6;
    border-radius: 16px;
}

QFrame#stat_card {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 10px;
}

QProgressBar {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    background: #e9ecef;
}

QProgressBar::chunk {
    background: #4361ee;
    border-radius: 4px;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
}

QScrollBar::handle:vertical {
    background: #ced4da;
    border-radius: 3px;
    min-height: 30px;
}
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class WordEntry:
    """단어장 한 행을 나타내는 데이터 클래스.

    UI와 완전히 분리되어 있어 모바일/웹 등 다른 프론트엔드에서도 재사용 가능.
    """
    word: str
    meaning: str
    word_type: str = "vocabulary"       # vocabulary | phrasal_verb | expression
    example: str = ""
    example_translation: str = ""
    label: str = "초기"                  # 초기 | 중기 | 장기
    needs_review: bool = True
    review_count: int = 0
    next_review: date = field(default_factory=date.today)
    memory_strength: int = 0
    added_date: date = field(default_factory=date.today)
    row_index: Optional[int] = None     # xlsx에서 읽어온 경우 행 번호 (1-based)

    WORD_TYPES = {
        "vocabulary": "단어",
        "phrasal_verb": "숙어",
        "expression": "표현",
    }

    LABELS = ["초기", "중기", "장기"]

    def type_display(self) -> str:
        return self.WORD_TYPES.get(self.word_type, self.word_type)

"""망각곡선 기반 복습 간격 계산 (SM-2 간소화 버전).

UI에 의존하지 않는 순수 로직 — 모바일/웹 재사용 가능.
"""
from datetime import date, timedelta
from data.models import WordEntry


_INTERVALS = [1, 3, 7, 14, 30, 60]   # 복습 횟수별 기본 간격 (일)
_STRENGTH_GAIN = 10                    # 정답 시 기억강도 증가량
_STRENGTH_PENALTY = 20                 # 오답 시 기억강도 감소량


def next_review_date(entry: WordEntry, correct: bool) -> date:
    """정답/오답 여부에 따라 다음 복습일 계산."""
    if not correct:
        return date.today() + timedelta(days=1)

    idx = min(entry.review_count, len(_INTERVALS) - 1)
    return date.today() + timedelta(days=_INTERVALS[idx])


def update_after_review(entry: WordEntry, correct: bool) -> WordEntry:
    """복습 결과를 반영해 WordEntry 업데이트 (새 객체 반환)."""
    new_count = entry.review_count + 1 if correct else max(0, entry.review_count - 1)
    new_strength = min(100, max(0, entry.memory_strength + (_STRENGTH_GAIN if correct else -_STRENGTH_PENALTY)))
    new_label = _compute_label(new_count)
    new_next = next_review_date(entry, correct)

    from dataclasses import replace
    return replace(
        entry,
        review_count=new_count,
        memory_strength=new_strength,
        label=new_label,
        next_review=new_next,
        needs_review=False,
    )


def get_due_entries(entries: list[WordEntry]) -> list[WordEntry]:
    """오늘 복습해야 할 단어 목록 반환."""
    today = date.today()
    return [e for e in entries if e.next_review <= today]


def _compute_label(review_count: int) -> str:
    if review_count >= 7:
        return "장기"
    if review_count >= 3:
        return "중기"
    return "초기"

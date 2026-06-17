"""퀴즈 로직 — UI에 의존하지 않는 순수 로직."""
import random
from dataclasses import dataclass
from data.models import WordEntry


@dataclass
class QuizQuestion:
    entry: WordEntry
    choices: list[str]      # 4지선다 보기 (뜻 기준)
    answer_index: int       # 정답 인덱스


def build_questions(entries: list[WordEntry], pool: list[WordEntry], count: int = 10) -> list[QuizQuestion]:
    """퀴즈 문제 생성.

    entries: 출제 대상 단어 목록
    pool: 오답 보기 후보 전체 목록
    """
    targets = random.sample(entries, min(count, len(entries)))
    questions = []
    for entry in targets:
        distractors = _pick_distractors(entry, pool, n=3)
        choices = distractors + [entry.meaning]
        random.shuffle(choices)
        answer_index = choices.index(entry.meaning)
        questions.append(QuizQuestion(entry=entry, choices=choices, answer_index=answer_index))
    return questions


def _pick_distractors(entry: WordEntry, pool: list[WordEntry], n: int) -> list[str]:
    candidates = [e.meaning for e in pool if e.word != entry.word]
    if len(candidates) < n:
        # 후보가 부족하면 중복 허용
        return random.choices(candidates, k=n) if candidates else ["(없음)"] * n
    return random.sample(candidates, n)

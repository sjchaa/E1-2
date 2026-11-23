
import json
import os

DATA_FILE = "state.json"

DEFAULT_QUIZZES = [
    {
        "question": "1 + 1 은 얼마일까요?",
        "choices": ["1", "2", "3", "4"],
        "answer": 2,
    },
    {
        "question": "바나나는 보통 무슨 색깔일까요?",
        "choices": ["노란색", "검은색", "파란색", "회색"],
        "answer": 1,
    },
    {
        "question": "다음 중 하늘을 날 수 있는 동물은 무엇일까요?",
        "choices": ["강아지", "참새", "거북이", "돼지"],
        "answer": 2,
    },
    {
        "question": "손가락은 한 손에 몇 개가 있을까요?",
        "choices": ["3개", "4개", "5개", "6개"],
        "answer": 3,
    },
    {
        "question": "밤하늘에서 빛나는 것은 무엇일까요?",
        "choices": ["별", "돌멩이", "책상", "양말"],
        "answer": 1,
    },
]

class Quiz:
    """퀴즈 한 문제를 표현하는 클래스"""

    def __init__(self, question: str, choices: list[str], answer: int):
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, index: int) -> None:
        print(f"\n[문제 {index}]")
        print(self.question)
        for idx, choice in enumerate(self.choices, start=1):
            print(f"{idx}. {choice}")

    def check_answer(self, user_choice: int) -> bool:
        return user_choice == self.answer

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=int(data["answer"]),
        )

class QuizGame:
    """퀴즈 게임 전체 진행과 파일 저장/불러오기를 담당하는 클래스"""

    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.quizzes: list[Quiz] = []
        self.best_score: int = 0
        self.load_data()

    def load_data(self) -> None:
        """state.json에서 퀴즈와 최고 점수를 불러오고, 없거나 깨지면 기본값으로 복구"""
        if not os.path.exists(self.filepath):
            self.quizzes = [Quiz.from_dict(item) for item in DEFAULT_QUIZZES]
            self.best_score = 0
            self.save_data()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)

            loaded_quizzes = raw.get("quizzes", [])
            if not isinstance(loaded_quizzes, list) or len(loaded_quizzes) == 0:
                raise ValueError("퀴즈 목록이 비어 있거나 형식이 올바르지 않습니다.")

            self.quizzes = [Quiz.from_dict(item) for item in loaded_quizzes]
            self.best_score = int(raw.get("best_score", 0))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as exc:
            print(f"⚠️ 데이터 파일 문제로 기본 퀴즈로 복구합니다. ({exc})")
            self.quizzes = [Quiz.from_dict(item) for item in DEFAULT_QUIZZES]
            self.best_score = 0
            self.save_data()

    def save_data(self) -> None:
        """현재 퀴즈 목록과 최고 점수를 state.json에 UTF-8로 저장"""
        payload = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
        }
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"⚠️ 파일 저장 중 오류가 발생했습니다: {exc}")


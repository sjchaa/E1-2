
import json # json 파일을 읽고 쓰는 기능을 가져옴
import os # 파일이 있는지 확인하거나 경로를 다룰 때 쓰는 명령

DATA_FILE = "state.json"

# state.json 이 없거나 손상되었을 때 사용할 퀴즈 5문항
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
    # self는 생성된 개별 퀴즈 객체 자신을 가리킴 (self.question 이 문제만의 질문)
    # __init__ : Quiz()로 새 퀴즈 객체를 만들 때 자동으로 실행되는 초기화 메서드
    def __init__(self, question: str, choices: list[str], answer: int):
        self.question = question # 문제 문자열
        self.choices = choices # 객관식 선택지 리스트 (기본 4개)
        self.answer = answer # 정답 번호(1~4)

    def display(self, index: int) -> None:
        # start=1 을 주어 보기가 0번이 아닌 1번부터 보이도록 출력
        print(f"\n[문제 {index}]")
        print(self.question)
        for idx, choice in enumerate(self.choices, start=1):
            print(f"{idx}. {choice}")

    def check_answer(self, user_choice: int) -> bool:
        # 입력한 번호가 정답 번호와 일치하는지 True/False로 변환
        return user_choice == self.answer
        # 사용자가 고른(choice) 번호와 정답(self.anser)이 같으면 True/다르면 False

    def to_dict(self) -> dict:
        # Quiz 객체를 JSON으로 저장할 수 있게 dict 형태로 변환
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        # dict 데이터를 읽어 Quiz 인스턴스를 생성(클래스 메서드)
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
        self.load_data() # 게임 시작 시 저장된 데이터 로드(없거나 깨지면 기본값 복구)

    def load_data(self) -> None:
        """state.json에서 퀴즈와 최고 점수를 불러오고, 없거나 깨지면 기본값으로 복구"""
        # 저장 파일이 없으면 기본 퀴즈로 초기화하고 파일 생성
        if not os.path.exists(self.filepath):
            self.quizzes = [Quiz.from_dict(item) for item in DEFAULT_QUIZZES]
            self.best_score = 0
            self.save_data()
            return

        try:
            # 한글 깨짐 방지를 위해 UTF-8 인코딩으로 읽기
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)

            loaded_quizzes = raw.get("quizzes", [])
            if not isinstance(loaded_quizzes, list) or len(loaded_quizzes) == 0:
                raise ValueError("퀴즈 목록이 비어 있거나 형식이 올바르지 않습니다.")

            self.quizzes = [Quiz.from_dict(item) for item in loaded_quizzes]
            self.best_score = int(raw.get("best_score", 0))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as exc:
            # 파일 손상이나 읽기 오류가 나도 프로그램이 멈추지 않고 기본 데이터로 복구
            print(f" 데이터 파일 문제로 기본 퀴즈로 복구합니다. ({exc})")
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
            # ensure_ascii=False로 한글 유지, indent=4로 가독성 있게 저장
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f" 파일 저장 중 오류가 발생했습니다: {exc}")


    @staticmethod
    def input_int_in_range(prompt: str, min_val: int, max_val: int) -> int:
        """공백 제거 및 예외 처리를 거쳐 min_val ~ max_val 사이 정수를 입력받음"""
        while True:
            raw = input(prompt).strip() # 앞뒤 공백 제거
            if not raw:
                print(" 빈 값입니다. 다시 입력하세요.")
                continue
            try:
                num = int(raw)
            except ValueError:
                # 숫자가 아닌 입력(예: abc)이 들어왔을 때 재입력 유도
                print(" 숫자를 입력하세요.")
                continue

            if min_val <= num <= max_val:
                return num
            print(f"{min_val}~{max_val} 사이의 숫자를 입력하세요.")


    def show_menu(self) -> None:
        # 메인 메뉴 출력
        print("\n" + "=" * 40)
        print(" 나만의 퀴즈 게임 ")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        total = len(self.quizzes)
        correct_count = 0
        print(f"\n 퀴즈를 시작합니다! (총 {total}문제)")

        for idx, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.display(idx)
            choice = self.input_int_in_range("정답 입력: ", 1, len(quiz.choices))
            if quiz.check_answer(choice):
                print(" 정답입니다!")
                correct_count += 1
            else:
                print(f" 오답입니다! (정답: {quiz.answer}번)")

        # 채점 방식(점수 계산) 변경 시 아래 계산식 및 최고 점수 갱신 로직을 수정
        score = int((correct_count / total) * 100)
        print("\n" + "=" * 40)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")

        if score > self.best_score:
            self.best_score = score
            self.save_data() # 최고 점수가 갱신되면 파일에 저장
            print(" 새로운 최고 점수입니다!")
        print("=" * 40)     

    def add_quiz(self) -> None:
            print("\n➕ 새 퀴즈 추가")
            while True:
                question = input("문제 입력: ").strip()
                if question:
                    break
                print(" 문제는 비워둘 수 없습니다.")
    
            choices = []
            # 선택지 개수를 바꾸려면 range(1, 5) 등 입력 및 검증 로직을 함께 수정
            for i in range(1, 5):
                while True:
                    opt = input(f"보기 {i} 입력: ").strip()
                    if opt:
                        choices.append(opt)
                        break
                    print(f" 보기 {i}는 비워둘 수 없습니다.")
    
            answer = self.input_int_in_range("정답 번호(1~4): ", 1, 4)
            self.quizzes.append(Quiz(question, choices, answer))
            self.save_data()
            print(" 새 퀴즈가 추가되고 state.json에 저장되었습니다!")     


    def show_quizzes(self) -> None:
        print("\n📚 등록된 퀴즈 목록")
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        for idx, q in enumerate(self.quizzes, start=1):
            print(f"\n[{idx}] {q.question}")
            for c_idx, c in enumerate(q.choices, start=1):
                mark = " (정답)" if c_idx == q.answer else ""
                print(f"   {c_idx}. {c}{mark}")

    def show_best_score(self) -> None:
        print("\n🏅 점수 확인")
        print(f"현재 최고 점수: {self.best_score}점")
        print(f"등록된 총 퀴즈 수: {len(self.quizzes)}문제")

    def run(self) -> None:
        # 5번(종료)을 선택할 때까지 메뉴 반복 실행
        while True:
            self.show_menu()
            choice = self.input_int_in_range("선택: ", 1, 5)
            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quizzes()
            elif choice == 4:
                self.show_best_score()
            elif choice == 5:
                print(" 게임을 종료합니다. 수고하셨습니다!")
                break


if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 게임 시작
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C나 입력 종료 시에도 데이터를 저장하고 안전하게 종료
        game.save_data()
        print("\n 입력이 중단되어 현재 데이터를 저장한 뒤 안전하게 종료합니다.")

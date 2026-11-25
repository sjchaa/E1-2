
import json # json 파일을 읽고 쓰는 기능을 가져옴
import os # 파일이 있는지 확인하거나 경로를 다룰 때 쓰는 명령
import shutil # 손상된 파일을 다른 이름으로 복사(백업)할 때 쓰는 명령
import signal # 프로그램을 끄라는 신호(SIGTERM)를 받았을 때 처리하는 명령

DATA_FILE = "state.json" # 퀴즈와 최고 점수를 저장할 파일 이름
BACKUP_FILE = "state_backup.json" # state.json이 손상됐을 때 원본을 복사해 둘 파일 이름

# state.json 이 없거나 손상되었을 때 사용할 퀴즈 5문항
# 퀴즈 하나는 dict(문제, 선택지, 정답)이고, 이 dict 5개를 list로 묶음
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
    # self는 생성된 개별 퀴즈 객체 자신을 가리킴 (self.question 이 그 문제만의 질문)
    # __init__ : Quiz()로 새 퀴즈 객체를 만들 때 자동으로 실행되는 초기화 메서드
    def __init__(self, question, choices, answer):
        self.question = question # 문제 문자열
        self.choices = choices # 객관식 선택지 리스트 (기본 4개)
        self.answer = answer # 정답 번호(1~4)

    def display(self, index):
        # 문제 번호, 문제, 선택지를 화면에 출력
        print(f"\n[문제 {index}]")
        print(self.question)
        # start=1 을 주어 보기가 0번이 아닌 1번부터 보이도록 출력
        for idx, choice in enumerate(self.choices, start=1):
            print(f"{idx}. {choice}")

    def check_answer(self, user_choice):
        # 사용자가 고른 번호(user_choice)와 정답(self.answer)이 같으면 True / 다르면 False
        return user_choice == self.answer

    def to_dict(self):
        # Quiz 객체를 JSON으로 저장할 수 있게 dict 형태로 변환
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        # dict 데이터를 읽어 Quiz 인스턴스를 생성(클래스 메서드)
        # cls는 Quiz 클래스 자신을 가리킴 → cls(...)는 Quiz(...)와 같음
        # 정답은 숫자로 비교해야 하므로 int()로 변환
        return cls(data["question"], data["choices"], int(data["answer"]))


class QuizGame:
    """퀴즈 게임 전체 진행과 파일 저장/불러오기를 담당하는 클래스"""

    def __init__(self):
        self.quizzes = [] # Quiz 객체들을 담아 둘 리스트
        self.best_score = None # 최고 점수 (아직 퀴즈를 한 번도 풀지 않았으면 None)
        self.load_data() # 게임 시작 시 저장된 데이터 로드(없거나 깨지면 기본값 복구)

    def use_default_quizzes(self):
        # 기본 퀴즈 5개(DEFAULT_QUIZZES)를 Quiz 객체로 바꿔서 퀴즈 목록으로 사용
        self.quizzes = [Quiz.from_dict(item) for item in DEFAULT_QUIZZES]
        self.best_score = None # 기본 퀴즈로 새로 시작하므로 점수 기록도 없음

    def load_data(self):
        """state.json에서 퀴즈와 최고 점수를 불러오고, 없거나 깨지면 기본값으로 복구"""
        # 저장 파일이 없으면(첫 실행) 기본 퀴즈로 초기화하고 파일 생성
        if not os.path.exists(DATA_FILE):
            print("저장된 데이터가 없어 기본 퀴즈 5개로 시작합니다.")
            self.use_default_quizzes()
            self.save_data()
            return # 파일을 읽을 필요가 없으므로 여기서 함수 종료

        try:
            # 한글 깨짐 방지를 위해 UTF-8 인코딩으로 읽기 ("r" = 읽기 모드)
            # with를 쓰면 다 읽은 뒤 파일을 자동으로 닫아 줌
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f) # JSON 파일 내용을 파이썬 dict로 바꿔서 가져옴

            # 파일에 저장된 퀴즈(dict)들을 하나씩 Quiz 객체로 바꿈
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            # 최고 점수를 가져옴 (키가 없으면 None)
            self.best_score = data.get("best_score")

            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개)")

        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as error:
            # 파일 손상이나 읽기 오류가 나도 프로그램이 멈추지 않고 기본 데이터로 복구
            # JSONDecodeError: JSON 문법이 깨짐 / KeyError: 필요한 값이 없음
            # TypeError, ValueError: 값의 형태가 이상함 / OSError: 파일을 읽을 수 없음
            print(f"데이터 파일에 문제가 있어 기본 퀴즈로 복구합니다. ({error})")
            # 기본 퀴즈로 덮어쓰기 전에, 손상된 원본을 백업 파일로 복사해 둠
            shutil.copy(DATA_FILE, BACKUP_FILE)
            print(f"손상된 원본은 {BACKUP_FILE} 파일로 백업했습니다.")
            self.use_default_quizzes()
            self.save_data()

    def save_data(self):
        """현재 퀴즈 목록과 최고 점수를 state.json에 UTF-8로 저장"""
        # Quiz 객체는 JSON에 바로 저장할 수 없으므로 to_dict()로 dict로 바꿈
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score, # None은 JSON 파일에 null로 저장됨
        }
        try:
            # "w" = 쓰기 모드 (기존 내용을 지우고 새로 씀)
            # ensure_ascii=False로 한글 유지, indent=4로 가독성 있게 저장
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError as error:
            # 저장할 수 없는 경우(권한 없음 등)에도 프로그램이 멈추지 않도록 처리
            print(f"파일 저장 중 오류가 발생했습니다: {error}")

    def input_number(self, prompt, min_num, max_num):
        """공백 제거 및 예외 처리를 거쳐 min_num ~ max_num 사이 정수를 입력받음"""
        # 올바른 숫자를 입력할 때까지 계속 반복 (몇 번 반복할지 모르므로 while 사용)
        while True:
            text = input(prompt).strip() # 앞뒤 공백 제거
            if text == "":
                # 아무것도 입력하지 않고 Enter만 누른 경우
                print("빈 값입니다. 다시 입력하세요.")
                continue # 아래 코드는 건너뛰고 다시 입력받음
            try:
                number = int(text) # 문자열을 숫자로 변환
            except ValueError:
                # 숫자가 아닌 입력(예: abc)이 들어왔을 때 재입력 유도
                print("숫자를 입력하세요.")
                continue
            if min_num <= number <= max_num:
                return number # 범위 안의 숫자면 그 숫자를 돌려주고 반복 종료
            # 범위 밖 숫자(예: 메뉴 9, 정답 0)인 경우
            print(f"{min_num}~{max_num} 사이의 숫자를 입력하세요.")

    def show_menu(self):
        # 메인 메뉴 출력
        print("\n" + "=" * 40)
        print("나만의 퀴즈 게임")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self):
        # 등록된 퀴즈가 하나도 없으면 안내 후 메뉴로 돌아감
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        total = len(self.quizzes) # 전체 문제 수
        correct_count = 0 # 맞힌 문제 수 (처음엔 0)
        print(f"\n퀴즈를 시작합니다! (총 {total}문제)")

        # 퀴즈 목록을 처음부터 끝까지 하나씩 출제 (문제 수만큼 반복하므로 for 사용)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.display(idx) # 문제와 선택지 출력
            choice = self.input_number("정답 입력: ", 1, 4) # 1~4 중 정답 입력받기
            if quiz.check_answer(choice):
                print("정답입니다!")
                correct_count += 1 # 맞히면 맞힌 개수 1 증가
            else:
                print(f"오답입니다! (정답: {quiz.answer}번)")

        # 채점 방식(점수 계산) 변경 시 아래 계산식 및 최고 점수 갱신 로직을 수정
        # 점수 = 맞힌 개수 ÷ 전체 문제 수 × 100 (int()로 소수점 버림)
        score = int(correct_count / total * 100)
        print("\n" + "=" * 40)
        print(f"결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")

        # 처음 푼 경우(None)이거나, 이번 점수가 최고 점수보다 높으면 갱신
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.save_data() # 최고 점수가 갱신되면 파일에 저장
            print("새로운 최고 점수입니다!")
        print("=" * 40)

    def add_quiz(self):
        print("\n새 퀴즈 추가")
        # 문제를 올바르게 입력할 때까지 입력받음
        while True:
            question = input("문제 입력: ").strip()
            # isprintable() : 화면에 정상적으로 표시되는 글자로만 되어 있으면 True
            # (한글 입력 중 글자가 깨지면 False → 파일 저장 오류를 막기 위해 다시 입력받음)
            if question != "" and question.isprintable():
                break # 빈 값이 아니고 깨진 글자가 없으면 반복 종료
            print("문제를 다시 입력하세요. (빈 값이나 깨진 글자는 사용할 수 없습니다)")

        choices = [] # 입력받은 선택지를 담을 리스트
        # 선택지 개수를 바꾸려면 range(1, 5) 등 입력 및 검증 로직을 함께 수정
        for i in range(1, 5): # i = 1, 2, 3, 4 → 선택지 4개 입력
            while True:
                choice = input(f"보기 {i} 입력: ").strip()
                # 문제 입력과 똑같이, 빈 값이거나 깨진 글자가 있으면 다시 입력받음
                if choice != "" and choice.isprintable():
                    choices.append(choice) # 리스트에 선택지 추가
                    break
                print(f"보기 {i} 내용을 다시 입력하세요. (빈 값이나 깨진 글자는 사용할 수 없습니다)")

        answer = self.input_number("정답 번호(1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer)) # 새 Quiz 객체를 만들어 목록에 추가
        self.save_data() # 추가한 퀴즈를 파일에 바로 저장
        print("새 퀴즈가 추가되고 state.json에 저장되었습니다!")

    def show_quizzes(self):
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        # 등록된 퀴즈가 없으면 안내 후 메뉴로 돌아감
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        # 퀴즈마다 문제와 선택지를 출력하고, 정답인 선택지 옆에 (정답) 표시
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{idx}] {quiz.question}")
            for c_idx, choice in enumerate(quiz.choices, start=1):
                mark = " (정답)" if c_idx == quiz.answer else "" # 정답 번호면 표시, 아니면 빈 문자열
                print(f"   {c_idx}. {choice}{mark}")

    def show_best_score(self):
        print("\n점수 확인")
        # 아직 퀴즈를 풀지 않았으면(None) 점수 대신 안내 문구 출력
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다.")
        else:
            print(f"최고 점수: {self.best_score}점")

    def run(self):
        # 5번(종료)을 선택할 때까지 메뉴 반복 실행
        while True:
            self.show_menu()
            choice = self.input_number("선택: ", 1, 5)
            # 선택한 번호에 따라 다른 기능 실행
            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quizzes()
            elif choice == 4:
                self.show_best_score()
            elif choice == 5:
                print("게임을 종료합니다. 수고하셨습니다!")
                break # while 반복을 빠져나가 프로그램 종료


def handle_sigterm(signum, frame):
    # 종료 신호(SIGTERM, 예: kill 명령)를 받으면 Ctrl+C를 누른 것과 똑같이 처리
    # → 아래 except (KeyboardInterrupt, EOFError) 부분에서 저장 후 종료하게 됨
    raise KeyboardInterrupt


if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 게임 시작
    signal.signal(signal.SIGTERM, handle_sigterm) # 종료 신호가 오면 handle_sigterm 함수 실행
    game = QuizGame() # 게임 객체 생성 (이때 __init__이 실행되어 데이터를 불러옴)
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, 입력 종료(EOF), 종료 신호(SIGTERM)가 와도 데이터를 저장하고 안전하게 종료
        game.save_data()
        print("\n프로그램이 중단되어 데이터를 저장하고 안전하게 종료합니다.")

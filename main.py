import json # JSON 파일을 읽고 쓰는 도구를 가져옴 (퀴즈 저장/불러오기에 사용)
import os # 파일이 있는지 없는지 확인하는 도구를 가져옴
import shutil # 파일을 복사하는 도구를 가져옴 (깨진 파일 백업에 사용)
import signal # 프로그램을 끄라는 신호(SIGTERM)를 받아서 처리하는 도구를 가져옴

# readline : 글자를 입력할 때 Backspace(지우기), 화살표 키를 똑똑하게 처리해 주는 도구
# 이걸 불러오지 않으면 한글을 지울 때 반쪽만 지워져서 글자가 깨질 수 있음
# 윈도우에는 readline이 없어서 오류(ImportError)가 나는데,
# 윈도우는 원래 한글이 잘 지워지므로 오류가 나면 그냥 넘어가도록(pass) 처리함
try:
    import readline
except ImportError:
    pass

DATA_FILE = "state.json" # 퀴즈와 최고 점수를 저장할 파일 이름
BACKUP_FILE = "state_backup.json" # 저장 파일이 깨졌을 때, 깨진 파일을 복사해 둘 백업 파일 이름

# 처음 실행할 때나 저장 파일이 깨졌을 때 쓰는 기본 퀴즈 5문제
# 퀴즈 하나 = { 문제, 보기 4개, 정답 번호 } 를 dict로 묶은 것
# 이 dict 5개를 다시 list [ ] 로 묶어서 퀴즈 목록을 만듦
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
    """퀴즈 '한 문제'를 만드는 설계도 (문제 카드 한 장이라고 생각하면 됨)"""

    # __init__ : Quiz(문제, 보기, 정답) 이렇게 새 퀴즈를 만들 때 자동으로 실행됨
    # self : 지금 만들어지는 '그 퀴즈 자기 자신'
    #        → 그래서 문제마다 자기만의 question, choices, answer 를 따로 가질 수 있음
    def __init__(self, question, choices, answer):
        self.question = question # 이 퀴즈의 문제 (글자)
        self.choices = choices # 이 퀴즈의 보기 4개 (리스트)
        self.answer = answer # 이 퀴즈의 정답 번호 (1~4 숫자)

    def display(self, index):
        # 문제 번호와 문제, 보기 4개를 화면에 보여 줌
        print(f"\n[문제 {index}]")
        print(self.question)
        # enumerate : 보기에 번호를 붙여서 하나씩 꺼내 줌
        # start=1 : 번호를 0이 아니라 1부터 붙임 → 1. 2. 3. 4.
        for idx, choice in enumerate(self.choices, start=1):
            print(f"{idx}. {choice}")

    def check_answer(self, user_choice):
        # 사용자가 고른 번호와 정답 번호가 같은지 확인
        # 같으면 True(정답), 다르면 False(오답)를 돌려줌
        return user_choice == self.answer

    def to_dict(self):
        # 퀴즈를 파일(JSON)에 저장할 수 있는 모양(dict)으로 바꿔 줌
        # (Quiz 객체는 JSON 파일에 바로 저장할 수 없어서 바꿔야 함)
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        # to_dict 의 반대 : 파일에서 읽어 온 dict 를 다시 Quiz 객체로 바꿔 줌
        # cls 는 Quiz 클래스 자신을 뜻함 → cls(...) 는 Quiz(...) 와 똑같음
        # int() : 정답은 숫자로 비교해야 하므로 혹시 글자로 저장돼 있어도 숫자로 바꿈
        return cls(data["question"], data["choices"], int(data["answer"]))


class QuizGame:
    """퀴즈 게임 '전체'를 진행하는 설계도 (문제 카드 묶음을 들고 게임을 진행하는 사람)"""

    def __init__(self):
        # 게임을 만들 때 자동으로 실행되어 처음 상태를 준비함
        self.quizzes = [] # Quiz 객체(문제 카드)들을 담아 둘 빈 리스트
        self.best_score = None # 최고 점수. None = '아직 한 번도 안 풀었음' (0점과 구분하려고)
        self.load_data() # 저장 파일에서 퀴즈와 최고 점수를 불러옴

    def use_default_quizzes(self):
        # 기본 퀴즈 5문제로 게임을 새로 시작할 때 사용
        # DEFAULT_QUIZZES 의 dict 를 하나씩 Quiz 객체로 바꿔서 퀴즈 목록에 넣음
        self.quizzes = [Quiz.from_dict(item) for item in DEFAULT_QUIZZES]
        self.best_score = None # 새로 시작하니까 점수 기록도 없음

    def load_data(self):
        """state.json 파일에서 퀴즈와 최고 점수를 불러옴 (없거나 깨졌으면 기본 퀴즈로 시작)"""

        # [경우 1] 저장 파일이 아예 없을 때 (처음 실행)
        if not os.path.exists(DATA_FILE):
            print("저장된 데이터가 없어 기본 퀴즈 5개로 시작합니다.")
            self.use_default_quizzes()
            self.save_data() # 기본 퀴즈로 저장 파일을 새로 만들어 둠
            return # 읽을 파일이 없으니 여기서 끝냄

        # try : 오류가 날 수도 있는 코드를 '일단 시도'해 봄
        try:
            # [경우 2] 저장 파일이 정상일 때
            # open(파일, "r") : 파일을 읽기(read) 모드로 엶
            # encoding="utf-8" : 한글이 깨지지 않게 읽음
            # with : 다 읽고 나면 파일을 자동으로 닫아 줌
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f) # JSON 파일 내용을 파이썬 dict 로 바꿔서 가져옴

            # 파일 안의 퀴즈(dict)들을 하나씩 Quiz 객체로 바꿔서 목록에 넣음
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            # 최고 점수를 가져옴 (저장된 값이 없으면 None)
            self.best_score = data.get("best_score")
            # 점수가 있으면 숫자(int)로 바꿈
            # → 점수가 "abc" 같은 글자로 잘못 저장돼 있으면 여기서 ValueError가 나서
            #   아래 except 로 넘어가 기본 퀴즈로 복구됨 (나중에 점수 비교할 때 멈추는 걸 막음)
            if self.best_score is not None:
                self.best_score = int(self.best_score)

            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개)")

        # except : try 안에서 아래 오류 중 하나가 나면, 멈추지 않고 이쪽으로 와서 처리함
        #   JSONDecodeError : JSON 문법이 깨짐 (따옴표, 쉼표가 빠졌을 때 등)
        #   KeyError        : 꼭 있어야 할 값이 없음 (예: "answer"가 없음)
        #   TypeError, ValueError : 값의 모양이 이상함 (예: 정답이 "abc")
        #   OSError         : 파일을 읽을 수 없음 (권한 문제 등)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as error:
            # [경우 3] 저장 파일이 깨졌을 때
            print(f"데이터 파일에 문제가 있어 기본 퀴즈로 복구합니다. ({error})")
            # 기본 퀴즈로 덮어쓰기 '전에' 깨진 파일을 백업 파일로 복사해 둠
            # → 나중에 원래 데이터를 되살릴 수 있게 하려고
            # 파일을 아예 읽을 수 없는 상황이면 복사도 실패할 수 있으므로 한 번 더 try 로 감쌈
            try:
                shutil.copy(DATA_FILE, BACKUP_FILE)
                print(f"손상된 원본은 {BACKUP_FILE} 파일로 백업했습니다.")
            except OSError:
                print("손상된 파일을 백업하지 못했습니다. (파일을 읽을 수 없음)")
            self.use_default_quizzes()
            self.save_data()

    def save_data(self):
        """지금의 퀴즈 목록과 최고 점수를 state.json 파일에 저장함"""
        # 저장할 내용을 dict 로 정리
        # Quiz 객체는 JSON에 바로 못 넣으므로 to_dict() 로 하나씩 dict 로 바꿈
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score, # None 은 파일에 null 로 저장됨
        }
        try:
            # open(파일, "w") : 파일을 쓰기(write) 모드로 엶 (기존 내용은 지우고 새로 씀)
            # ensure_ascii=False : 한글을 그대로 저장 (안 하면 \uXXXX 같은 이상한 글자로 저장됨)
            # indent=4 : 사람이 보기 좋게 4칸씩 들여쓰기해서 저장
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError as error:
            # 저장에 실패해도(폴더 쓰기 권한이 없을 때 등) 프로그램이 멈추지 않게 안내만 함
            print(f"파일 저장 중 오류가 발생했습니다: {error}")

    def input_number(self, prompt, min_num, max_num):
        """min_num ~ max_num 사이의 숫자를 입력받음 (잘못 입력하면 올바르게 넣을 때까지 다시 물어봄)"""
        # 매개변수(함수에 넣어 주는 재료)
        #   prompt  : 화면에 보여 줄 안내 문구 (예: "선택: ")
        #   min_num : 허용하는 가장 작은 숫자
        #   max_num : 허용하는 가장 큰 숫자
        # 사용자가 몇 번 틀릴지 모르니까, 올바른 값이 나올 때까지 while 로 계속 반복
        while True:
            text = input(prompt).strip() # strip() : 앞뒤 공백을 지움 (" 1 " → "1")

            # 1) 아무것도 안 쓰고 Enter 만 누른 경우
            if text == "":
                print("빈 값입니다. 다시 입력하세요.")
                continue # continue : 아래는 건너뛰고 while 처음으로 돌아가 다시 입력받음

            # 2) 숫자가 아닌 글자(예: abc)를 입력한 경우
            try:
                number = int(text) # 입력은 항상 글자(str)라서 숫자(int)로 바꿔 봄
            except ValueError: # "abc" 처럼 숫자로 못 바꾸면 ValueError 오류가 남
                print("숫자를 입력하세요.")
                continue

            # 3) 범위 안의 숫자면 그 숫자를 돌려주고(return) 반복을 끝냄
            if min_num <= number <= max_num:
                return number

            # 4) 범위 밖의 숫자(예: 메뉴에 없는 9, 정답에 없는 0)인 경우
            print(f"{min_num}~{max_num} 사이의 숫자를 입력하세요.")

    def show_menu(self):
        # 메인 메뉴를 화면에 보여 줌 ("=" * 40 은 = 를 40개 이어 붙인 줄)
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
        # 퀴즈가 하나도 없으면 풀 게 없으니 안내하고 메뉴로 돌아감
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        total = len(self.quizzes) # 전체 문제 수
        correct_count = 0 # 맞힌 문제 수 (처음에는 0개)
        print(f"\n퀴즈를 시작합니다! (총 {total}문제)")

        # 퀴즈를 처음부터 끝까지 하나씩 냄
        # 문제 수만큼 정해진 횟수를 반복하므로 for 를 사용
        for idx, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.display(idx) # 문제와 보기를 보여 줌
            choice = self.input_number("정답 입력: ", 1, 4) # 1~4 중에서 답을 입력받음

            # 정답인지 확인해서 결과를 알려 줌
            if quiz.check_answer(choice):
                print("정답입니다!")
                correct_count += 1 # 맞혔으면 맞힌 개수를 1 늘림
            else:
                print(f"오답입니다! (정답: {quiz.answer}번)")

        # 점수 계산 : 맞힌 개수 ÷ 전체 문제 수 × 100
        # int() 로 소수점은 버림 (예: 83.33 → 83)
        # ※ 점수 계산 방법을 바꾸고 싶으면 이 줄을 고치면 됨
        score = int(correct_count / total * 100)
        print("\n" + "=" * 40)
        print(f"결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")

        # 최고 점수 바꾸기
        # 처음 푼 경우(None)이거나, 이번 점수가 기존 최고 점수보다 높을 때만 바꿈
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.save_data() # 바뀐 최고 점수를 파일에 바로 저장
            print("새로운 최고 점수입니다!")
        print("=" * 40)

    def add_quiz(self):
        print("\n새 퀴즈 추가")

        # 1) 문제 입력받기 (올바르게 입력할 때까지 반복)
        while True:
            question = input("문제 입력: ").strip()
            # isprintable() : 화면에 정상적으로 보이는 글자로만 되어 있으면 True
            #                 한글이 깨져서 이상한 글자가 섞여 있으면 False
            # → 깨진 글자가 파일에 저장되면 오류가 나기 때문에 미리 걸러 냄
            if question != "" and question.isprintable():
                break # 빈 값도 아니고 깨진 글자도 없으면 반복을 끝냄
            print("문제를 다시 입력하세요. (빈 값이나 깨진 글자는 사용할 수 없습니다)")

        # 2) 보기 4개 입력받기
        choices = [] # 입력받은 보기를 하나씩 담을 빈 리스트
        # range(1, 5) : 1, 2, 3, 4 → 보기 4개를 차례로 입력받음
        # ※ 보기 개수를 바꾸고 싶으면 이 숫자와 정답 번호 범위(1, 4)를 같이 고쳐야 함
        for i in range(1, 5):
            while True:
                choice = input(f"보기 {i} 입력: ").strip()
                # 문제 입력과 똑같이, 빈 값이나 깨진 글자면 다시 입력받음
                if choice != "" and choice.isprintable():
                    choices.append(choice) # append : 리스트 맨 뒤에 보기를 추가
                    break
                print(f"보기 {i} 내용을 다시 입력하세요. (빈 값이나 깨진 글자는 사용할 수 없습니다)")

        # 3) 정답 번호 입력받기 (1~4만 허용)
        answer = self.input_number("정답 번호(1~4): ", 1, 4)

        # 4) 입력받은 내용으로 새 Quiz 객체를 만들어 목록 맨 뒤에 추가하고 바로 저장
        self.quizzes.append(Quiz(question, choices, answer))
        self.save_data()
        print("새 퀴즈가 추가되고 state.json에 저장되었습니다!")

    def show_quizzes(self):
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        # 퀴즈가 하나도 없으면 안내하고 메뉴로 돌아감
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        # 퀴즈마다 문제와 보기를 보여 주고, 정답인 보기 옆에 (정답) 표시를 붙임
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{idx}] {quiz.question}")
            for c_idx, choice in enumerate(quiz.choices, start=1):
                # 보기 번호가 정답 번호와 같으면 " (정답)", 아니면 빈 글자 ""
                mark = " (정답)" if c_idx == quiz.answer else ""
                print(f"   {c_idx}. {choice}{mark}")

    def show_best_score(self):
        print("\n점수 확인")
        # 아직 한 번도 안 풀었으면(None) 점수 대신 안내 문구를 보여 줌
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다.")
        else:
            print(f"최고 점수: {self.best_score}점")

    def run(self):
        # 게임의 시작점 : 5번(종료)을 누를 때까지 메뉴를 계속 반복해서 보여 줌
        # 언제 종료할지 모르니까 while True 로 반복
        while True:
            self.show_menu()
            choice = self.input_number("선택: ", 1, 5) # 1~5 중에서 메뉴 번호를 입력받음

            # 고른 번호에 따라 다른 기능을 실행 (if / elif)
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
                break # break : while 반복을 빠져나감 → 프로그램 종료


def handle_sigterm(signum, frame):
    # SIGTERM : 다른 곳에서 "이 프로그램 꺼라" 하고 보내는 신호 (예: kill 명령)
    # 이 신호를 받으면 Ctrl+C 를 누른 것(KeyboardInterrupt)과 똑같이 바꿔 줌
    # → 그러면 맨 아래 except 부분에서 저장하고 안전하게 끝나게 됨
    raise KeyboardInterrupt


# 이 파일을 직접 실행했을 때만(python3 main.py) 아래 코드가 실행됨
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm) # 종료 신호가 오면 handle_sigterm 을 실행하도록 등록
    game = QuizGame() # 게임 객체를 만듦 (이때 __init__ 이 실행되어 저장된 데이터를 불러옴)
    try:
        game.run() # 게임 시작
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 를 누르거나(KeyboardInterrupt), 입력이 끊기거나(EOFError),
        # 종료 신호(SIGTERM)를 받아도 프로그램이 그냥 꺼지지 않고
        # 지금까지의 데이터를 저장한 뒤 안전하게 종료함
        game.save_data()
        print("\n프로그램이 중단되어 데이터를 저장하고 안전하게 종료합니다.")

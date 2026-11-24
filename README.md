
# 나만의 퀴즈 게임

Python 표준 라이브러리와 객체 지향(`Quiz`, `QuizGame`) 구조로 구현한 터미널 기반 퀴즈 게임입니다. `state.json`을 통해 퀴즈 목록과 최고 점수를 영속적으로 저장하며, 잘못된 입력과 파일 오류에 대한 예외 처리를 포함합니다.

## 1. 프로젝트 개요

* **목적** : 동작하는 프로그램인 퀴즈 게임을 직접 구현하고
 그 과정 속에서 `Python` 기초 문법과, 클래스 설계, `state.json` 파일 입출력, 예외 처리, 그리고 `Git` 기반 버전 관리를 익히고 스스로 설명할 수 있도록 만든 프로젝트입니다.


## 2. 퀴즈 주제 선정 이유

* **주제**: 누구나 풀 수 있는 초간단 기초 상식 퀴즈 (기본 5문항)


* **선정 이유**: 복잡한 배경지식 없이 바로 답을 맞힐 수 있는 간단하고 쉬운 문제들로 구성했습니다. 퀴즈 풀이, 새 퀴즈 추가, 점수 계산, `state.json` 저장·복구 흐름을 빠르고 직관적으로 테스트하기 위해서입니다.


## 3. 파일 구조

```text
E1-2/
├── .gitignore       # 불필요한 파일 및 캐시 Git 추적 제외 설정
├── main.py          # Quiz, QuizGame 클래스 및 CLI 게임 실행 로직
├── README.md        # 프로젝트 설명 및 사용 가이드
└── state.json       # 퀴즈 목록 및 최고 점수 저장 파일 (실행 시 생성/갱신)
```

## 4. 실행 방법

### 사전 요구사항
* **Python 3.10 이상** (CLI 환경 / WSL 또는 터미널)

### 실행 명령어

프로젝트 루트 디렉터리에서 아래 명령어(`python3 main.py`)로 프로그램을 실행하거나, VScode에서 재생 버튼을 눌러 바로 실행합니다.


```bash
git clone <https://github.com/sjchaa/E1-2.git>
cd E1-2
python3 --version   # 3.10 이상인지 확인
python3 main.py
```

또는 VS Code에서 `main.py`를 열고 우측 상단 ▶(Run Python File) 버튼을 눌러 실행합니다.


```
sj_ee_6255@GNIA-C202-K01:~/E1-2$ python3 main.py

========================================
🎯 나만의 퀴즈 게임 🎯
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
========================================
선택: 
```

또는

vs code 이미지 첨부


### 터미널 실행 로그

**메인 메뉴 & 잘못된 입력 처리**
```text
$ python3 main.py

========================================
 나만의 퀴즈 게임
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
========================================
선택: abc
 숫자를 입력하세요.
선택:
 빈 값입니다. 다시 입력하세요.
선택: 9
1~5 사이의 숫자를 입력하세요.
선택:  1      ← 앞뒤 공백은 제거되어 1로 처리
```

**퀴즈 풀기**
```text
 퀴즈를 시작합니다! (총 5문제)
----------------------------------------

[문제 1]
1 + 1 은 얼마일까요?
1. 1
2. 2
3. 3
4. 4
정답 입력: 2
 정답입니다!
... (중략) ...
========================================
🏆 결과: 5문제 중 5문제 정답! (100점)
 새로운 최고 점수입니다!
========================================
```

**점수 확인**
```text
선택: 4

🏅 점수 확인
현재 최고 점수: 100점
등록된 총 퀴즈 수: 5문제
```

**손상된 state.json 복구**
```text
$ echo '{broken' > state.json
$ python3 main.py
 데이터 파일 문제로 기본 퀴즈로 복구합니다. (Expecting property name enclosed in double quotes: line 1 column 2 (char 1))
 손상된 원본은 state.json.broken_20261124_231604.bak 로 백업했습니다.
 원본을 되살리려면 백업 파일을 수정한 뒤 state.json 으로 이름을 바꾸세요.
```

**종료 신호(SIGTERM) / 입력 종료(EOF) 처리**
```text
$ kill -TERM <PID>     # 다른 터미널에서 실행
 종료 신호(SIGTERM)를 받아 데이터를 저장한 뒤 종료합니다.

$ python3 main.py < /dev/null
 입력이 중단되어 현재 데이터를 저장한 뒤 안전하게 종료합니다.
```

## 5. 기능 목록

| 기능 | 설명 | 담당 메서드 |
|---|---|---|
| 메뉴 및 흐름 제어 | 메인 메뉴 출력, 번호 선택, 5번(종료) 선택 전까지 반복 | `show_menu()`, `run()` |
| 퀴즈 풀기 | 저장된 퀴즈 순차 출제, 정답(1~4) 입력, 정·오답 안내, 결과·점수 표시, 퀴즈가 없을 때 안내 | `play_quiz()` |
| 퀴즈 추가 | 문제·선택지 4개·정답 번호 입력 및 빈 값 검증 후 목록 추가·저장 | `add_quiz()` |
| 퀴즈 목록 | 문제, 선택지, 정답 표시. 퀴즈가 없을 때 안내 | `show_quizzes()` |
| 점수 확인 | 최고 점수와 등록된 퀴즈 수 표시. 풀이 후 최고 점수 비교·갱신·저장 | `show_best_score()`, `play_quiz()` |
| 입력 검증 | 앞뒤 공백 제거, 빈 입력·문자·범위 밖 숫자 입력 시 안내 후 재입력 | `input_int_in_range()` |
| 저장/불러오기 | `state.json` UTF-8 저장·로드, 파일이 없으면 기본 퀴즈 사용 | `save_data()`, `load_data()` |
| 손상 파일 복구 | 손상 시 원본을 `.bak`로 백업한 뒤 기본 퀴즈로 복구 | `load_data()`, `backup_broken_file()` |
| 안전 종료 | `Ctrl+C`, `EOFError`, `SIGTERM`/`SIGHUP` 발생 시 저장 후 종료 | `__main__` 블록, `register_signal_handlers()` |

## 6. 설계: 클래스를 사용한 이유

프로그램을 **"퀴즈 한 문제"** 와 **"게임 전체"** 라는 두 개의 역할로 나누었습니다.

| 클래스 | 역할 | 속성 | 주요 메서드 |
|---|---|---|---|
| `Quiz` | 퀴즈 한 문제의 데이터와 동작 | `question`, `choices`, `answer` | `display()`, `check_answer()`, `to_dict()`, `from_dict()` |
| `QuizGame` | 퀴즈 목록·최고 점수 관리, 메뉴 진행, 파일 저장/불러오기 | `filepath`, `quizzes`, `best_score` | `run()`, `play_quiz()`, `add_quiz()`, `show_quizzes()`, `show_best_score()`, `load_data()`, `save_data()` |

* **추상화**: 문제·선택지·정답을 각각 따로 된 변수나 dict로 다루지 않고 `Quiz` 객체 하나로 묶었습니다. 그래서 `QuizGame`은 `quiz.display()`, `quiz.check_answer(choice)`만 호출하면 되고, 문제가 어떻게 출력되고 채점되는지 내부 구현을 알 필요가 없습니다.
* **재사용성**: 기본 퀴즈 5개, 사용자가 추가한 퀴즈, `state.json`에서 불러온 퀴즈가 모두 같은 `Quiz` 클래스로 만들어집니다. 출력·채점·저장 형식 변환(`to_dict`/`from_dict`)을 한 곳에 정의해 두었기 때문에 퀴즈가 몇 개로 늘어나도 같은 코드를 그대로 재사용합니다.
* **책임 분리 (유지보수)**: 문제 출력 형식을 바꾸고 싶으면 `Quiz.display()`만, 저장 방식을 바꾸고 싶으면 `QuizGame.save_data()`/`load_data()`만 수정하면 됩니다. 수정 범위가 좁아져 다른 기능을 실수로 망가뜨릴 위험이 줄어듭니다.
* **`__init__`과 `self`**: `__init__`은 `Quiz(...)`로 객체를 만들 때 자동 실행되어 속성을 초기화하고, `self`는 "지금 이 객체 자신"을 가리켜 문제마다 서로 다른 `question`, `answer`를 가질 수 있게 합니다.

## 7. 파일 구조

```text
E1-2/
├── .gitignore              # 캐시(__pycache__), 임시·백업 파일(*.tmp, *.bak) Git 추적 제외
├── main.py                 # Quiz, QuizGame 클래스 및 CLI 게임 실행 로직
├── README.md               # 프로젝트 설명 및 사용 가이드
├── state.json              # 퀴즈 목록 및 최고 점수 저장 파일 (실행 시 생성/갱신)
└── docs/
    └── screenshots/        # 실행 화면, git log 그래프, clone/pull 실습 스크린샷
```

## 8. 데이터 파일 설명 (state.json)

### 경로와 역할
* **경로**: 프로젝트 루트의 `state.json` (`main.py`의 `DATA_FILE` 상수로 지정)
* **인코딩**: UTF-8 (`ensure_ascii=False`로 한글을 그대로 저장, `indent=4`로 사람이 읽기 쉽게 저장)
* **역할**: 프로그램을 종료하고 다시 실행해도 **추가한 퀴즈와 최고 점수가 유지**되도록 하는 영속 저장소
* **저장 시점**: 최초 실행(파일이 없을 때), 퀴즈 추가 직후, 최고 점수 갱신 직후, 정상/비정상 종료 시

### 스키마

```json
{
    "quizzes": [
        {
            "question": "1 + 1 은 얼마일까요?",
            "choices": ["1", "2", "3", "4"],
            "answer": 2
        }
    ],
    "best_score": 100
}
```

| 키 | 타입 | 설명 |
|---|---|---|
| `quizzes` | `list[dict]` | 퀴즈 목록. 비어 있으면 손상된 것으로 보고 기본 퀴즈로 복구 |
| `quizzes[].question` | `str` | 문제 내용 |
| `quizzes[].choices` | `list[str]` | 선택지 4개 |
| `quizzes[].answer` | `int` | 정답 번호 (1~4, 1부터 시작) |
| `best_score` | `int` | 최고 점수 (0~100점, 정답률 기준) |

### JSON을 저장 형식으로 선택한 이유
* **가독성**: 텍스트 파일이라 편집기로 바로 열어 내용을 확인·수정할 수 있고, 디버깅할 때 저장 상태를 눈으로 확인하기 쉽습니다.
* **구조화**: 퀴즈 목록(리스트)과 각 퀴즈의 문제·선택지·정답(딕셔너리)이라는 중첩 구조를 Python의 `list`/`dict`와 1:1로 그대로 표현할 수 있습니다. 반면 `.txt`는 구분자 규칙을 직접 만들어야 하고, CSV는 선택지 같은 리스트를 한 칸에 담기 어렵습니다.
* **표준 라이브러리 지원**: 외부 라이브러리 없이 `json.dump()`/`json.load()`만으로 저장·불러오기가 가능합니다.
* **범용성**: 언어에 독립적인 표준 형식이라 다른 프로그램이나 웹에서도 같은 데이터를 그대로 읽을 수 있습니다.
* **안전성**: `pickle`과 달리 데이터만 담고 코드를 실행하지 않으므로, 파일을 불러올 때 임의 코드가 실행될 위험이 없습니다.

## 9. 예외 처리와 안전 종료

### 입력 예외 (`input_int_in_range()`)
| 입력 예 | 처리 |
|---|---|
| ` 1 ` (앞뒤 공백) | `strip()`으로 공백 제거 후 `1`로 처리 |
| 빈 입력 (Enter) | "빈 값입니다. 다시 입력하세요." 후 재입력 |
| `abc` | `int()` 변환 실패(`ValueError`) → "숫자를 입력하세요." 후 재입력 |
| `9` (메뉴), `0` (정답) | "1~5(1~4) 사이의 숫자를 입력하세요." 후 재입력 |

### 파일 예외 (`load_data()` / `save_data()`)
| 상황 | 처리 |
|---|---|
| `state.json` 없음 (첫 실행) | 기본 퀴즈 5개로 시작하고 파일 생성 |
| JSON 문법 오류, 키 누락, 타입 오류, 빈 퀴즈 목록 | `try/except`로 잡아 안내 메시지 출력 → **원본 백업** → 기본 퀴즈로 복구 후 저장 |
| 저장 중 디스크·권한 오류 (`OSError`) | 오류 메시지 출력, 프로그램은 계속 실행 |

### 손상 파일 백업 및 복구 절차
1. `load_data()`가 손상을 감지하면 덮어쓰기 **전에** `backup_broken_file()`이 원본을 `state.json.broken_YYYYMMDD_HHMMSS.bak`로 복사합니다. (시각이 붙어 여러 번 손상돼도 이전 백업이 덮어써지지 않음)
2. 화면에 오류 원인과 백업 파일 경로를 안내합니다.
3. 기본 퀴즈로 복구한 새 `state.json`을 저장하고 게임을 계속합니다.
4. **사용자가 원본을 되살리려면**: 백업 파일을 편집기로 열어 JSON 오류(위 안내 메시지의 줄/열 위치)를 고친 뒤 `state.json`으로 이름을 바꾸고 다시 실행합니다.
   ```bash
   mv state.json.broken_20261124_231604.bak state.json
   python3 main.py
   ```

또한 `save_data()`는 `state.json.tmp`에 먼저 쓴 뒤 `os.replace()`로 교체합니다. 저장 도중 프로그램이 종료되더라도 기존 `state.json`이 반쯤 쓰인 상태로 손상되지 않습니다.

### 안전 종료
| 종료 원인 | 처리 위치 | 동작 |
|---|---|---|
| 메뉴 5번 | `run()` | 종료 메시지 출력 후 반복문 탈출 |
| `Ctrl+C` (`KeyboardInterrupt`) | `__main__`의 `try/except` | 저장 후 안내 메시지 출력 |
| 입력 스트림 종료 (`EOFError`, `Ctrl+D`) | `__main__`의 `try/except` | 저장 후 안내 메시지 출력 |
| `SIGTERM` (`kill` 명령, 작업 관리자 종료 등) | `register_signal_handlers()` | 저장 후 `sys.exit(0)`으로 정상 종료 |
| `SIGHUP` (터미널 창 닫힘, Linux/macOS) | `register_signal_handlers()` | 저장 후 정상 종료 (Windows에는 없는 신호라 `hasattr`로 확인 후 등록) |

> `SIGKILL`(`kill -9`)은 운영체제가 프로세스를 강제로 끝내는 신호라 프로그램이 가로챌 수 없습니다. 이 경우를 대비해 퀴즈 추가·최고 점수 갱신 **직후** 바로 저장하도록 했습니다.

## 10. 요구사항 변경 시 수정 지점

| 변경하고 싶은 것 | 수정할 위치 |
|---|---|
| 점수 계산 방식 (예: 100점 만점 → 정답 개수) | `QuizGame.play_quiz()`의 `score = int((correct_count / total) * 100)`, `show_best_score()` 출력 문구 |
| 최고 점수 갱신 조건 | `QuizGame.play_quiz()`의 `if score > self.best_score:` |
| 선택지 개수 (4개 → 5개) | `QuizGame.add_quiz()`의 `range(1, 5)`와 `input_int_in_range("정답 번호(1~4): ", 1, 4)`, `DEFAULT_QUIZZES`의 `choices` |
| 기본 퀴즈 내용·주제 | 파일 상단 `DEFAULT_QUIZZES` 리스트 |
| 문제 출력 형식 | `Quiz.display()` |
| 정답 판정 방식 (예: 복수 정답) | `Quiz.check_answer()`, `Quiz.answer` 타입, `to_dict()`/`from_dict()` |
| 퀴즈에 새 속성 추가 (예: 힌트) | `Quiz.__init__()`, `to_dict()`, `from_dict()`, `add_quiz()` 입력 부분 |
| 메뉴 항목 추가 (예: 퀴즈 삭제) | `QuizGame.show_menu()`, `run()`의 `if/elif`와 `input_int_in_range("선택: ", 1, 5)`의 범위 |
| 입력 검증 규칙 / 안내 문구 | `QuizGame.input_int_in_range()` |
| 저장 파일 경로·형식 | `DATA_FILE` 상수, `QuizGame.load_data()`, `save_data()` |
| 손상 파일 처리 방식 | `QuizGame.load_data()`의 `except` 블록, `backup_broken_file()` |
| 종료 신호 처리 | `register_signal_handlers()`, `__main__` 블록 |

## 11. 대량 데이터 확장 시 성능 고려

현재 구조는 **프로그램 시작 시 `state.json` 전체를 메모리에 읽고, 저장할 때마다 전체를 다시 쓰는** 방식입니다. 퀴즈가 1,000개 이상으로 늘어날 때를 가정해 아래 샘플 벤치마크를 측정했습니다.

### 샘플 벤치마크
* 측정 방법: 문제·선택지 4개·정답을 가진 퀴즈 N개를 만들어 현재 코드와 같은 옵션(`ensure_ascii=False, indent=4`)으로 `json.dump`/`json.load`, `tracemalloc`으로 불러오기 시 최대 메모리 측정, 마지막 문제를 리스트에서 순차 검색
* 측정 환경: Linux x86_64, Python 3.13 (실행 환경에 따라 수치는 달라질 수 있음)

| 퀴즈 수 | 파일 크기 | 전체 저장 | 전체 불러오기 | 불러오기 메모리(peak) | 순차 검색(마지막 문제) |
|---|---|---|---|---|---|
| 5 | 1.3 KB | < 10 ms | 0.2 ms | 0.01 MB | 0.001 ms 미만 |
| 1,000 | 261 KB | 4 ms | 5 ms | 1.0 MB | 0.03 ms |
| 10,000 | 2.6 MB | 38 ms | 57 ms | 10.3 MB | 0.34 ms |
| 100,000 | 26 MB | 498 ms | 706 ms | 103.5 MB | 4.8 ms |

### 분석
* 저장·불러오기 시간과 메모리는 퀴즈 수에 **비례(O(n))** 해서 늘어납니다. 퀴즈 1개당 약 260 B(파일), 약 1 KB(메모리)입니다.
* **1,000~10,000개**: 저장·불러오기 모두 0.1초 이내라 사용자가 체감할 지연이 없어 현재 구조로 충분합니다.
* **100,000개 이상**: 퀴즈 1개만 추가해도 26 MB 파일 전체를 다시 쓰느라 약 0.5초가 걸리고, 메모리도 100 MB를 넘습니다. 이 시점부터 개선이 필요합니다.
* 퀴즈 풀기는 순서대로 출제하므로 검색이 필요 없고, 목록 출력은 화면 출력 자체가 병목이 됩니다.

### 규모별 대응 방안
| 규모 | 방안 |
|---|---|
| ~1만 개 | 현재 구조 유지 (`indent=4` 제거 시 파일 크기 약 25% 감소 가능) |
| 목록이 길어질 때 | `show_quizzes()`에 페이지 단위 출력(예: 20개씩) 적용 |
| 문제 검색·삭제 기능 추가 시 | `{문제 ID: Quiz}` 딕셔너리 인덱스를 함께 두어 O(n) 순차 검색을 O(1) 조회로 개선 |
| 10만 개 이상 | 표준 라이브러리 `sqlite3`로 전환해 추가한 퀴즈 1건만 저장(INSERT), 필요한 문제만 조회(SELECT)하여 메모리 사용 최소화 |

## 12. Git 작업 기록

### 커밋 규칙
**커밋 단위**: 하나의 커밋에는 하나의 기능 또는 하나의 수정만 담습니다. (메뉴 → Quiz 클래스 → 기본 데이터 → 퀴즈 풀기 → 추가 → 목록 → 점수 → 저장 → README 순서)

**메시지 템플릿**
```text
<타입>: <변경 내용 요약 (무엇을 했는지)>

(선택) 본문: 왜 변경했는지, 무엇이 달라졌는지
```

| 타입 | 사용 시점 | 예시 |
|---|---|---|
| `Feat` | 새 기능 추가 | `Feat: 퀴즈 풀기 기능 구현` |
| `Fix` | 버그 수정 | `Fix: 점수 계산 오류 수정` |
| `Docs` | 문서 수정 | `Docs: README 실행 방법 추가` |
| `Refactor` | 동작 변화 없는 구조 개선 | `Refactor: QuizGame 책임 분리` |
| `Chore` | 설정·환경 파일 | `Chore: .gitignore 추가` |

### 원격 저장소 및 커밋 로그
* **저장소 URL**: <YOUR_GITHUB_URL>

```text
$ git log --oneline --graph
(여기에 실제 git log --oneline --graph 결과를 붙여넣으세요)
```

![git log graph](docs/screenshots/git_log_graph.png)

### 브랜치 생성 및 병합 기록
퀴즈 풀기 기능은 `main`이 아닌 별도 브랜치에서 개발한 뒤 병합했습니다.

```bash
git checkout -b feature/play-quiz     # 브랜치 생성 및 이동
# ... 퀴즈 풀기 기능 구현 ...
git add main.py
git commit -m "Feat: 퀴즈 풀기 기능 구현"
git checkout main                     # main으로 복귀
git merge feature/play-quiz           # 병합
git push origin main
```

![브랜치 병합 그래프](docs/screenshots/git_branch_merge.png)

### clone / pull 실습
개발 완료 후 다른 위치에서 저장소를 복제해 수정하고, 기존 작업 폴더에서 pull로 변경 사항을 받아왔습니다.

```bash
# 1) 별도 디렉터리에 clone
cd ~
git clone <YOUR_GITHUB_URL> E1-2-clone
cd E1-2-clone

# 2) 복제본에서 README 한 줄 수정 후 commit → push
echo "- clone 실습으로 추가한 줄" >> README.md
git add README.md
git commit -m "Docs: clone 실습으로 README 한 줄 추가"
git push origin main

# 3) 기존 작업 디렉터리에서 pull
cd ~/E1-2
git pull origin main

# 4) 반영 확인
git log --oneline -3
tail -1 README.md
```

| 단계 | 스크린샷 |
|---|---|
| clone 및 복제본에서 commit/push | ![clone](docs/screenshots/git_clone_push.png) |
| 기존 폴더에서 pull 및 반영 확인 | ![pull](docs/screenshots/git_pull.png) |

### 사용한 Git 명령어
| 명령어 | 역할 | 사용 시점 |
|---|---|---|
| `git init` | 현재 폴더를 Git 저장소로 초기화 | 프로젝트 시작 |
| `git add` | 변경 파일을 커밋 대기 영역(stage)에 올림 | 매 커밋 전 |
| `git commit` | stage된 변경을 이력으로 기록 | 기능 단위 완료 시 |
| `git push` | 로컬 커밋을 GitHub에 업로드 | 커밋 후 |
| `git checkout` | 브랜치 생성(`-b`)·이동 | 퀴즈 풀기 기능 개발 |
| `git merge` | 다른 브랜치의 변경을 현재 브랜치에 합침 | 퀴즈 풀기 완료 후 |
| `git clone` | 원격 저장소를 새 폴더로 복제 | clone/pull 실습 |
| `git pull` | 원격 변경을 가져와 현재 브랜치에 병합 | clone/pull 실습 |

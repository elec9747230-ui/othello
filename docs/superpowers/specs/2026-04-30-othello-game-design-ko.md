# 오델로 게임 — 설계 스펙

- 일자: 2026-04-30
- 상태: 승인됨 (브레인스토밍 완료)
- 프로젝트 성격: 학습용 프로젝트 (클린 아키텍처 연습)

## 1. 개요

Python + Tkinter 로 오델로(리버시) 데스크톱 게임을 구현합니다. 1차 목표는 클린 아키텍처 연습 — 게임 로직, AI 전략, UI 를 명확히 분리해 각 계층이 독립적으로 테스트 가능하고 교체 가능하도록 만드는 것입니다.

게임은 2인 로컬 대전과 4단계 난이도 AI 대전(Random, Greedy, Minimax, 가중치 평가 기반 Alpha-Beta)을 지원합니다. 보드 크기는 6×6 / 8×8 / 10×10 중 선택할 수 있습니다.

## 2. 목표

- Tkinter GUI 로 동작하는 완전한 플레이 가능 오델로 게임.
- UI / AI 의존성이 없는 순수 Python 코어 엔진 — 단위 테스트 가능.
- 단일 `Strategy` 인터페이스를 공유하는 4종 AI 전략 (다형성 학습용).
- UX 편의 기능: 합법수 표시, 점수, undo, hint, 수순 기록(history), 저장/불러오기, 애니메이션, 효과음.
- 매직 넘버 없이 보드 크기(6/8/10)를 자유롭게 변경 가능.

## 3. 비목표 (Out of Scope)

- 온라인 멀티플레이어 / 네트워킹.
- 모바일 / 웹 타깃.
- 토너먼트급 AI (예: MCTS, 딥러닝).
- 단일 언어를 넘어선 다국어 지원.
- 커스텀 테마 / 스킨.

## 4. 제약 조건

- Python 3.10+ (`dataclasses`, `match`, `Enum`, type hint, ABC 사용).
- 표준 라이브러리 우선. 외부 의존성은 다음으로 제한:
  - `playsound` (효과음, 크로스플랫폼)
  - `pytest` (테스트, dev 전용)
- Tkinter 는 Python 기본 포함 — 별도 GUI 의존성 없음.
- 크로스플랫폼 (Windows / macOS / Linux).

## 5. 아키텍처

3계층 구조이며 의존 방향은 단방향:

```
ui/  →  ai/  →  core/
        ai/  ────→ core/
```

- `core/` 는 `ai/` 나 `ui/` 의 어떤 것도 import 하지 않습니다.
- `ai/` 는 `core/` 만 import 합니다.
- `ui/` 는 양쪽에서 import 하며, Tkinter / playsound 를 import 하는 유일한 계층입니다.

### 5.1 프로젝트 레이아웃

```
othello/
├── README.md
├── requirements.txt              # playsound; pytest 는 [dev]
├── main.py                       # 진입점
├── othello/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── board.py              # Board, Color, Move
│   │   ├── rules.py              # legal_moves, apply_move, is_terminal, winner, score
│   │   └── game.py               # GameState (history, undo, auto-pass)
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py               # Strategy ABC
│   │   ├── random_ai.py
│   │   ├── greedy.py
│   │   ├── minimax.py
│   │   ├── alphabeta.py
│   │   └── evaluation.py         # weighted_position_score, generic_score
│   ├── persistence.py            # save_game, load_game (JSON)
│   └── ui/
│       ├── __init__.py
│       ├── app.py                # Tk root, 화면 전환
│       ├── menu_screen.py
│       ├── game_screen.py
│       ├── board_view.py         # Canvas 렌더링, 애니메이션
│       └── sound.py              # playsound 래퍼
├── assets/
│   └── sounds/
│       ├── place.wav
│       ├── flip.wav
│       └── win.wav
├── savegames/                    # 런타임, .gitignore 처리
└── tests/
    ├── test_rules.py
    ├── test_game.py
    └── test_ai.py
```

## 6. 코어 엔진 (`core/`)

### 6.1 보드 표현

8×8 (또는 N×N) 크기의 **2D 리스트**, 각 칸은 `Color` enum. 속도보다 명확성을 우선해 선택했습니다.

```python
class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color": ...

@dataclass(frozen=True)
class Move:
    row: int
    col: int

# pass 용 모듈 레벨 상수:
PASS: Move  # 센티넬; 예: Move(-1, -1)
```

`Board` 가 노출하는 인터페이스:
- `Board(size: int = 8)` — 표준 4 중앙 돌로 초기화. `size` 가 홀수이거나 4 미만이면 `ValueError`.
- `size: int`
- `__getitem__((r, c)) -> Color` / `__setitem__`
- `copy() -> Board`
- `cells() -> Iterator[tuple[int, int, Color]]`

### 6.2 규칙 (`rules.py`) — 순수 함수

```python
def legal_moves(board: Board, color: Color) -> list[Move]
def apply_move(board: Board, move: Move, color: Color) -> Board   # 새 보드 반환
def is_terminal(board: Board) -> bool
def winner(board: Board) -> Color | None                           # None = 무승부
def score(board: Board) -> tuple[int, int]                         # (black_count, white_count)
```

**불변성:** `apply_move` 는 새로운 `Board` 를 반환하며 원본을 절대 변형하지 않습니다. 이유:
- AI 탐색 트리에 자연스러움 (재귀 안에서 undo 할 필요 없음).
- `GameState` 수준의 undo 가 단순해짐 (역연산 없이 상태 교체만).
- 학습 목표인 함수형 규율을 강화.

### 6.3 GameState (`game.py`)

게임 진행과 history 를 소유합니다.

```python
@dataclass
class HistoryEntry:
    board_before: Board
    color_to_move: Color
    move: Move

class GameState:
    board: Board
    current: Color
    history: list[HistoryEntry]

    def __init__(self, size: int = 8): ...

    def legal_moves(self) -> list[Move]
    def must_pass(self) -> bool                # 본인 합법수가 없고 상대는 있을 때
    def is_over(self) -> bool                  # 양쪽 모두 합법수가 없을 때
    def play(self, move: Move) -> None         # rules 에 위임; history 추가; auto-pass 처리
    def undo(self) -> None                     # history pop, 보드+턴 복원
    def score(self) -> tuple[int, int]
    def winner(self) -> Color | None
```

**Auto-pass 동작:** `play` 직후 다음 플레이어에게 합법수가 없지만 방금 둔 플레이어에게는 합법수가 남아 있다면 턴이 다시 같은 색으로 돌아옵니다 (history 에 `Move.PASS` 가 기록됨). 양쪽 모두 합법수가 없으면 `is_over()` 가 True.

## 7. AI 계층 (`ai/`)

### 7.1 Strategy 인터페이스

```python
class Strategy(ABC):
    name: str

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """state.legal_moves() 안에 있는 합법수를 반환해야 합니다. 합법수가 없으면 예외."""
```

UI 는 AI 종류로 분기하지 않고 항상 `strategy.select_move(state)` 를 호출합니다. Hint 도 동일 인터페이스를 재사용합니다 (설정된 Strategy 를 호출해 반환된 수를 hint 마커로 표시).

### 7.2 구현체

| 클래스 | 모듈 | 동작 |
|---|---|---|
| `RandomAI` | `random_ai.py` | 합법수 중 균등 무작위 |
| `GreedyAI` | `greedy.py` | 즉시 뒤집는 돌 수가 최대인 수 |
| `MinimaxAI` | `minimax.py` | 깊이 제한 Minimax, 기본 깊이 3 |
| `AlphaBetaAI` | `alphabeta.py` | Alpha-Beta 가지치기, 기본 깊이 5 |

`MinimaxAI` 와 `AlphaBetaAI` 는 생성자에 `depth: int` 파라미터를 받습니다 (위 기본값).

### 7.3 평가 함수 (`evaluation.py`)

```python
def evaluate(board: Board, color: Color) -> int
```

보드 크기에 따라 디스패치:
- **8×8:** `weighted_position_score` — 표준 가중치 테이블 (코너 +100, X-square -25, 가장자리 +10 등).
- **6×6 / 10×10 / 그 외:** `generic_score` — 코너 +30, 가장자리 +5, 내부 +1, 상대 색은 부호 반전.

종료 시 (빈 칸 없음 또는 양쪽 모두 합법수 없음): 돌 개수 차이를 기준으로 큰 양/음수 반환.

## 8. UI 계층 (`ui/`)

### 8.1 화면 흐름

```
Menu Screen ──Start──▶ Game Screen
     ▲                      │
     └────"Back to Menu"────┘
     │
     └────"Load Game"───────▶ Game Screen
```

`app.py` 가 `Tk` root 를 소유하며 `Frame` 화면들을 `pack_forget()` / `pack()` 으로 전환합니다.

### 8.2 메뉴 화면

컨트롤:
- 모드: 2-Player / vs AI (라디오)
- AI 난이도: Random / Greedy / Minimax / Alpha-Beta (vs AI 일 때만 활성)
- 사용자 색상: Black / White (vs AI 일 때만 활성)
- 보드 크기: 6 / 8 / 10
- 버튼: [Start], [Load Saved Game]

### 8.3 게임 화면

레이아웃:
```
┌────────────────────────┬──────────────┐
│                        │ Turn: ● BLACK │
│                        │ Score: ●3 ○3  │
│      Board Canvas      │              │
│   (size × size grid)   │ [Undo]       │
│                        │ [Hint]       │
│                        │ [Save]       │
│                        │ [Menu]       │
└────────────────────────┴──────────────┘
                         History: 1.d3 2.c5 ...
```

### 8.4 보드 렌더링 (`board_view.py`)

- `tkinter.Canvas` 로 셀 사각형과 돌 타원을 그립니다.
- 합법수: 현재 플레이어가 둘 수 있는 빈 칸에 작은 점 또는 반투명 링 표시.
- 클릭 핸들러: 픽셀 `(x, y)` → `(row, col)` 매핑 후 `controller.try_play(Move(row, col))` 호출.
- 캔버스는 보드 크기에 비례해 리사이즈.

### 8.5 애니메이션

모든 애니메이션은 UI 계층에 존재하며 `core/` 에는 애니메이션 개념이 없습니다.

- **돌 배치:** 0% → 100% 로 ~150ms 동안 확대.
- **뒤집기:** 색상 크로스페이드 또는 가로 폭을 줄였다 늘리며 회전을 모방, 돌 1개당 ~200ms, 같은 수에 뒤집히는 돌들 사이 ~30ms 시차.
- 애니메이션 동안 `is_animating` 플래그로 클릭을 막습니다. AI 수는 애니메이션 종료 후에만 스케줄됩니다.

### 8.6 효과음 (`sound.py`)

`playsound` 래퍼:
- 돌 배치 시 `play_place()`.
- 뒤집힌 돌마다 `play_flip()` (또는 수 한 번에 한 번 — 구현 시 결정. 둘 다 허용).
- 종료 상태에서 `play_win()`.

재생 실패 (파일 누락, 오디오 사용 불가) 가 게임을 크래시시키면 안 됩니다 — try/except 로 감싸고 로그만 남깁니다.

### 8.7 AI 턴 처리

`state.current` 가 AI 일 때:
1. 진행 중인 애니메이션이 끝날 때까지 대기.
2. 입력 비활성화.
3. `root.after(300, run_ai)` 로 짧게 보이는 지연 후 실행 스케줄.
4. `run_ai` 가 `strategy.select_move(state)` 를 동기 호출, 수를 두고, 애니메이션 트리거.

8×8 깊이 5 Alpha-Beta 까지는 동기 처리로 충분합니다. 체감 가능한 지연이 발생하면 AI 호출을 백그라운드 스레드로 옮기지만, 1차 구현은 동기로 갑니다.

## 9. 영속화 (`persistence.py`)

저장 포맷 (JSON):

```json
{
  "version": 1,
  "size": 8,
  "current": "BLACK",
  "mode": "vs_ai",
  "ai_difficulty": "alphabeta",
  "human_color": "BLACK",
  "history": [
    {"row": 2, "col": 3, "color": "BLACK"},
    {"row": 2, "col": 4, "color": "WHITE"}
  ]
}
```

**보드 스냅샷이 아닌 history 기반:** 로드 시 빈 보드에 규칙으로 수를 재생(replay)해 파일 내용과 무관하게 규칙에 맞는 상태를 보장합니다. 파일이 작고 사람이 읽기 쉬우며 향후 기보(notation) 내보내기로 자연스럽게 확장 가능합니다.

API:
```python
def save_game(state: GameState, mode_info: dict, path: Path) -> None
def load_game(path: Path) -> tuple[GameState, dict]
```

기본적으로 저장은 `savegames/` 아래에 타임스탬프 파일명으로 저장하며, 사용자는 파일 다이얼로그로 경로를 직접 선택할 수 있습니다.

로드 실패 시 (파일 손상, 버전 불일치, replay 중 불법수): 메시지박스로 에러 표시 후 현재 화면 유지.

## 10. 테스트

테스트 러너는 `pytest` 만 사용합니다. 테스트 대상은 `core/` + `ai/` 만 포함합니다.

| 파일 | 커버리지 |
|---|---|
| `test_rules.py` | 6/8/10 크기 초기 보드; 8방향 합법수 계산; 뒤집기 정확성; 종료/승자; pass 조건 |
| `test_game.py` | `play` → `undo` 라운드트립 시 보드+턴 복원; auto-pass; `is_over` 종료; history 무결성 |
| `test_ai.py` | 모든 Strategy 가 합법수만 반환; Greedy 가 뒤집는 수를 최대화; 같은 깊이의 Minimax 와 AlphaBeta 가 동일한 수 선택 (가지치기 정확성 검증) |

`pytest` 를 프로젝트 루트에서 Tkinter 가 설치되지 않은 환경에서도 통과해야 합니다 (즉, `core/` 와 `ai/` 의 import 경로가 Tkinter 를 transitive 하게라도 import 하면 안 됨).

## 11. 에러 처리

- **잘못된 클릭** (합법수가 아닌 빈 칸 또는 점유된 칸): UI 단에서 조용히 무시. 합법수 표시가 이미 사용자를 안내합니다.
- **저장 파일 손상 / 버전 불일치:** 에러 다이얼로그, 메뉴 화면으로 복귀.
- **합법수가 없는 상태에서 Strategy 호출:** GameState 의 auto-pass 덕에 도달 불가. `assert` 로 가드.
- **사운드 재생 실패:** catch 후 로그만, 절대 크래시하지 않음.

## 12. 미해결 항목 / 향후 작업

1차 버전 범위 외이지만 기록해둘 만한 것들:

- 메뉴에서 난이도별 깊이 조절 (현재는 깊이 3 / 5 고정).
- 느린 머신에서 깊이 5 Alpha-Beta 가 lag 시 AI 스레드 분리.
- 표준 기보 / notation 으로 게임 내보내기.
- 보드 색상 / 돌 스타일 테마.
- 저장된 history 를 단계별로 재생하는 replay 모드.

## 13. 요약

깔끔하고 계층화된 오델로 구현: 순수 함수형 코어, 다형성 AI, 애니메이션과 사운드를 가진 Tkinter UI. 학습 프로젝트 범위에 맞춰 명확성, 테스트 가능성, 향후 확장성을 모두 고려해 설계했습니다.

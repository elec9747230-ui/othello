# 오델로 게임 구현 계획서

> **에이전트 작업자용:** 필수 서브 스킬 — superpowers:subagent-driven-development(권장) 또는 superpowers:executing-plans 를 사용해 Task 단위로 구현합니다. 각 단계는 체크박스(`- [ ]`) 문법으로 추적합니다.

**목표:** [docs/superpowers/specs/2026-04-30-othello-game-design.md](../specs/2026-04-30-othello-game-design.md) 의 계층형 아키텍처를 따라, Python + Tkinter 로 동작하는 완전한 데스크톱 오델로 게임을 구현합니다.

**아키텍처:** 3계층(`core/` → `ai/` → `ui/`) 구조이며 의존 방향은 단방향입니다. 순수 함수형 `core/` 엔진은 UI/AI에 의존하지 않고, `ai/` 계층은 다형성 전략을 추가하며, `ui/` 계층만이 Tkinter와 사운드를 직접 다룹니다.

**기술 스택:** Python 3.10+, Tkinter(stdlib), `playsound`(사운드), `pytest`(테스트).

---

## 파일 구성

이 계획서는 다음 파일들을 생성/수정합니다. 각 Task는 그중 한정된 영역만 다룹니다.

```
othello/
├── .gitignore                       # Task 1
├── README.md                        # Task 1 (뼈대), Task 22 (보강)
├── requirements.txt                 # Task 1
├── main.py                          # Task 15
├── othello/
│   ├── __init__.py                  # Task 1 (빈 파일)
│   ├── core/
│   │   ├── __init__.py              # Task 1 (빈 파일)
│   │   ├── board.py                 # Task 2, Task 3
│   │   ├── rules.py                 # Task 4, Task 5, Task 6
│   │   └── game.py                  # Task 7, Task 8
│   ├── ai/
│   │   ├── __init__.py              # Task 9 (빈 파일)
│   │   ├── base.py                  # Task 9
│   │   ├── random_ai.py             # Task 9
│   │   ├── greedy.py                # Task 10
│   │   ├── evaluation.py            # Task 11
│   │   ├── minimax.py               # Task 12
│   │   └── alphabeta.py             # Task 13
│   ├── persistence.py               # Task 14
│   └── ui/
│       ├── __init__.py              # Task 15 (빈 파일)
│       ├── app.py                   # Task 15
│       ├── menu_screen.py           # Task 16
│       ├── board_view.py            # Task 17, Task 19
│       ├── game_screen.py           # Task 18, Task 21
│       └── sound.py                 # Task 20
└── tests/
    ├── __init__.py                  # Task 1 (빈 파일)
    ├── test_board.py                # Task 2, Task 3
    ├── test_rules.py                # Task 4, Task 5, Task 6
    ├── test_game.py                 # Task 7, Task 8
    ├── test_ai.py                   # Task 9, 10, 12, 13
    ├── test_evaluation.py           # Task 11
    └── test_persistence.py          # Task 14
```

UI 파일(Task 15–21)은 스펙 §10 에 따라 자동화 테스트가 없으며, 대신 수동 스모크 테스트로 검증합니다.

---

## Task 1: 프로젝트 스캐폴딩

디렉터리 구조, 패키징 파일을 만들고 Python 환경을 검증합니다.

**파일:**
- 생성: `othello/.gitignore`
- 생성: `othello/requirements.txt`
- 생성: `othello/README.md`
- 생성: `othello/othello/__init__.py` (빈 파일)
- 생성: `othello/othello/core/__init__.py` (빈 파일)
- 생성: `othello/tests/__init__.py` (빈 파일)

- [ ] **Step 1: Python 3.10+ 설치 확인**

실행: `python --version`

기대 결과: `Python 3.10.x` 이상. 만약 `C:\Users\elec9\AppData\Local\Microsoft\WindowsApps\python.exe` 의 Microsoft Store 스텁(즉시 종료, exit code 49)이 잡히면 https://python.org 에서 정식 Python을 설치한 뒤 셸을 새로 엽니다. 이후 단계는 `python` 이 실제 Python 3.10+ 인터프리터로 해석된다고 가정합니다.

- [ ] **Step 2: Tkinter 확인 및 venv 생성**

`c:/Users/elec9/othello/` 에서 실행:
```bash
python -c "import tkinter; print('tkinter OK')"
python -m venv .venv
source .venv/Scripts/activate    # Windows의 Git-Bash 기준
python -m pip install --upgrade pip
```

기대 결과: `tkinter OK` 출력, `.venv/` 디렉터리 생성, pip 업그레이드 성공.

- [ ] **Step 3: requirements 작성 및 pytest 설치**

`c:/Users/elec9/othello/requirements.txt` 생성:
```
playsound==1.3.0
```

이어서 개발 도구 설치:
```bash
pip install -r requirements.txt
pip install pytest
```

기대 결과: 둘 다 에러 없이 설치. (Windows 에서 `playsound` 가 GStreamer 의존성으로 실패하면 주석 처리해도 됩니다 — Task 20 의 사운드 래퍼가 import 실패를 무시합니다.)

- [ ] **Step 4: .gitignore 작성**

`c:/Users/elec9/othello/.gitignore` 생성:
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
savegames/
```

- [ ] **Step 5: 빈 패키지 디렉터리 생성**

다음 파일들을 빈 파일로 만듭니다:
- `c:/Users/elec9/othello/othello/__init__.py`
- `c:/Users/elec9/othello/othello/core/__init__.py`
- `c:/Users/elec9/othello/tests/__init__.py`

- [ ] **Step 6: README 뼈대 작성**

`c:/Users/elec9/othello/README.md` 생성:
```markdown
# Othello

A desktop Othello (Reversi) game in Python with Tkinter.

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design.

## Run

```
python main.py
```

## Test

```
pytest
```
```

- [ ] **Step 7: 테스트 없이 pytest 실행 확인**

실행: `pytest`

기대 결과: exit code 5 (`no tests ran`) 또는 0 + "0 collected". 둘 다 정상. pytest 가 실행되지 않으면 venv 를 다시 활성화합니다.

- [ ] **Step 8: 커밋**

```bash
git add othello/__init__.py othello/core/__init__.py tests/__init__.py .gitignore requirements.txt README.md
git commit -m "chore: scaffold Othello project structure"
```

---

## Task 2: Color enum 과 Move 데이터클래스

**파일:**
- 생성: `othello/othello/core/board.py`
- 생성: `othello/tests/test_board.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_board.py` 생성:
```python
import pytest
from othello.core.board import Color, Move, PASS


def test_color_opponent_swaps():
    assert Color.BLACK.opponent() is Color.WHITE
    assert Color.WHITE.opponent() is Color.BLACK


def test_color_empty_has_no_opponent():
    with pytest.raises(ValueError):
        Color.EMPTY.opponent()


def test_move_is_pass_sentinel():
    assert PASS.is_pass is True
    assert Move(0, 0).is_pass is False


def test_move_is_frozen():
    m = Move(2, 3)
    with pytest.raises(Exception):
        m.row = 5  # frozen dataclass
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_board.py -v`

기대 결과: `ModuleNotFoundError: No module named 'othello.core.board'` 로 실패.

- [ ] **Step 3: Color, Move, PASS 구현**

`c:/Users/elec9/othello/othello/core/board.py` 생성:
```python
from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color":
        if self is Color.BLACK:
            return Color.WHITE
        if self is Color.WHITE:
            return Color.BLACK
        raise ValueError("Color.EMPTY has no opponent")


@dataclass(frozen=True)
class Move:
    row: int
    col: int

    @property
    def is_pass(self) -> bool:
        return self.row == -1 and self.col == -1


PASS: Move = Move(-1, -1)
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_board.py -v`

기대 결과: 4 passed.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/board.py tests/test_board.py
git commit -m "feat(core): add Color enum and Move dataclass"
```

---

## Task 3: Board 클래스

**파일:**
- 수정: `othello/othello/core/board.py`
- 수정: `othello/tests/test_board.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_board.py` 끝에 추가:
```python
from othello.core.board import Board


def test_board_default_size_is_8():
    b = Board()
    assert b.size == 8


def test_board_rejects_odd_size():
    with pytest.raises(ValueError):
        Board(size=7)


def test_board_rejects_too_small():
    with pytest.raises(ValueError):
        Board(size=2)


def test_board_initial_position_8x8():
    b = Board(size=8)
    # 표준 오델로 초기 배치
    assert b[3, 3] is Color.WHITE
    assert b[4, 4] is Color.WHITE
    assert b[3, 4] is Color.BLACK
    assert b[4, 3] is Color.BLACK
    # 나머지는 모두 빈 칸
    empties = sum(1 for _, _, c in b.cells() if c is Color.EMPTY)
    assert empties == 60


def test_board_initial_position_6x6():
    b = Board(size=6)
    assert b[2, 2] is Color.WHITE
    assert b[3, 3] is Color.WHITE
    assert b[2, 3] is Color.BLACK
    assert b[3, 2] is Color.BLACK


def test_board_setitem_and_getitem():
    b = Board()
    b[0, 0] = Color.BLACK
    assert b[0, 0] is Color.BLACK


def test_board_copy_is_independent():
    b = Board()
    c = b.copy()
    c[0, 0] = Color.BLACK
    assert b[0, 0] is Color.EMPTY


def test_board_in_bounds():
    b = Board(size=8)
    assert b.in_bounds(0, 0)
    assert b.in_bounds(7, 7)
    assert not b.in_bounds(-1, 0)
    assert not b.in_bounds(0, 8)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_board.py -v`

기대 결과: 새로 추가된 8개 테스트가 `ImportError: cannot import name 'Board'` 로 실패.

- [ ] **Step 3: Board 구현**

`c:/Users/elec9/othello/othello/core/board.py` 끝에 추가:
```python
from typing import Iterator


class Board:
    def __init__(self, size: int = 8):
        if size < 4 or size % 2 != 0:
            raise ValueError(f"Board size must be even and >= 4, got {size}")
        self.size = size
        self._cells: list[list[Color]] = [
            [Color.EMPTY] * size for _ in range(size)
        ]
        m = size // 2
        self._cells[m - 1][m - 1] = Color.WHITE
        self._cells[m][m] = Color.WHITE
        self._cells[m - 1][m] = Color.BLACK
        self._cells[m][m - 1] = Color.BLACK

    def __getitem__(self, rc: tuple[int, int]) -> Color:
        r, c = rc
        return self._cells[r][c]

    def __setitem__(self, rc: tuple[int, int], color: Color) -> None:
        r, c = rc
        self._cells[r][c] = color

    def copy(self) -> "Board":
        new = Board.__new__(Board)
        new.size = self.size
        new._cells = [row[:] for row in self._cells]
        return new

    def cells(self) -> Iterator[tuple[int, int, Color]]:
        for r in range(self.size):
            for c in range(self.size):
                yield (r, c, self._cells[r][c])

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_board.py -v`

기대 결과: 12 passed.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/board.py tests/test_board.py
git commit -m "feat(core): add Board class with N×N initial position"
```

---

## Task 4: 규칙 — `legal_moves` 와 `flips_for`

**파일:**
- 생성: `othello/othello/core/rules.py`
- 생성: `othello/tests/test_rules.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_rules.py` 생성:
```python
from othello.core.board import Board, Color, Move
from othello.core.rules import legal_moves, flips_for


def test_initial_black_has_four_legal_moves():
    b = Board()
    moves = legal_moves(b, Color.BLACK)
    expected = {Move(2, 3), Move(3, 2), Move(4, 5), Move(5, 4)}
    assert set(moves) == expected


def test_initial_white_has_four_legal_moves():
    b = Board()
    moves = legal_moves(b, Color.WHITE)
    expected = {Move(2, 4), Move(4, 2), Move(3, 5), Move(5, 3)}
    assert set(moves) == expected


def test_flips_for_initial_black_d3():
    b = Board()
    flips = flips_for(b, Move(2, 3), Color.BLACK)
    # BLACK이 (2,3)에 두면 (3,3)의 WHITE를 뒤집습니다.
    assert flips == [(3, 3)]


def test_flips_for_illegal_move_returns_empty():
    b = Board()
    # (0,0)은 아무것도 뒤집지 못함
    assert flips_for(b, Move(0, 0), Color.BLACK) == []
    # 이미 점유된 칸
    assert flips_for(b, Move(3, 3), Color.BLACK) == []


def test_flips_for_multidirectional():
    # 표준 초기 상태에서 BLACK이 (4,5)에 두면 (4,4)의 WHITE를 뒤집습니다.
    b = Board()
    flips = flips_for(b, Move(4, 5), Color.BLACK)
    assert flips == [(4, 4)]


def test_legal_moves_empty_when_no_captures_possible():
    b = Board(size=4)  # 4x4 초소형 보드
    # 빈 4x4 보드에서도 양쪽 모두 합법수가 존재해야 합니다.
    assert len(legal_moves(b, Color.BLACK)) > 0
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_rules.py -v`

기대 결과: 모두 `ModuleNotFoundError` 로 실패.

- [ ] **Step 3: `flips_for` 와 `legal_moves` 구현**

`c:/Users/elec9/othello/othello/core/rules.py` 생성:
```python
from othello.core.board import Board, Color, Move

DIRECTIONS: list[tuple[int, int]] = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def _flips_in_direction(
    board: Board, r: int, c: int, dr: int, dc: int, color: Color
) -> list[tuple[int, int]]:
    opp = color.opponent()
    captured: list[tuple[int, int]] = []
    rr, cc = r + dr, c + dc
    while board.in_bounds(rr, cc) and board[rr, cc] is opp:
        captured.append((rr, cc))
        rr += dr
        cc += dc
    if board.in_bounds(rr, cc) and board[rr, cc] is color and captured:
        return captured
    return []


def flips_for(board: Board, move: Move, color: Color) -> list[tuple[int, int]]:
    """`color`가 `move`에 두었을 때 뒤집힐 상대 돌의 좌표 목록을 반환.
    빈 리스트면 불법수입니다."""
    if not board.in_bounds(move.row, move.col):
        return []
    if board[move.row, move.col] is not Color.EMPTY:
        return []
    all_flips: list[tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        all_flips.extend(
            _flips_in_direction(board, move.row, move.col, dr, dc, color)
        )
    return all_flips


def legal_moves(board: Board, color: Color) -> list[Move]:
    moves: list[Move] = []
    for r in range(board.size):
        for c in range(board.size):
            if board[r, c] is Color.EMPTY:
                m = Move(r, c)
                if flips_for(board, m, color):
                    moves.append(m)
    return moves
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_rules.py -v`

기대 결과: 6 passed.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add legal_moves and flips_for"
```

---

## Task 5: 규칙 — `apply_move`

**파일:**
- 수정: `othello/othello/core/rules.py`
- 수정: `othello/tests/test_rules.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_rules.py` 끝에 추가:
```python
import pytest
from othello.core.rules import apply_move


def test_apply_move_returns_new_board():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b is not b
    # 원본은 변경되지 않아야 합니다.
    assert b[2, 3] is Color.EMPTY
    assert b[3, 3] is Color.WHITE


def test_apply_move_places_stone_and_flips():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b[2, 3] is Color.BLACK
    assert new_b[3, 3] is Color.BLACK  # WHITE에서 뒤집힘


def test_apply_move_raises_on_illegal_move():
    b = Board()
    with pytest.raises(ValueError):
        apply_move(b, Move(0, 0), Color.BLACK)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_rules.py -v -k apply_move`

기대 결과: 3개 테스트가 `ImportError: cannot import name 'apply_move'` 로 실패.

- [ ] **Step 3: `apply_move` 구현**

`c:/Users/elec9/othello/othello/core/rules.py` 끝에 추가:
```python
def apply_move(board: Board, move: Move, color: Color) -> Board:
    flips = flips_for(board, move, color)
    if not flips:
        raise ValueError(f"Illegal move {move} for {color.name}")
    new_board = board.copy()
    new_board[move.row, move.col] = color
    for r, c in flips:
        new_board[r, c] = color
    return new_board
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_rules.py -v`

기대 결과: 9 passed total.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add apply_move (immutable)"
```

---

## Task 6: 규칙 — `score`, `is_terminal`, `winner`

**파일:**
- 수정: `othello/othello/core/rules.py`
- 수정: `othello/tests/test_rules.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_rules.py` 끝에 추가:
```python
from othello.core.rules import score, is_terminal, winner


def test_score_initial_is_2_2():
    b = Board()
    assert score(b) == (2, 2)


def test_score_after_first_black_move():
    b = Board()
    b2 = apply_move(b, Move(2, 3), Color.BLACK)
    # BLACK은 4개(놓은 1 + 뒤집힌 1 + 기존 2), WHITE는 1개
    assert score(b2) == (4, 1)


def test_is_terminal_initial_is_false():
    assert is_terminal(Board()) is False


def test_is_terminal_full_board_is_true():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    assert is_terminal(b) is True


def test_winner_full_black_board():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    assert winner(b) is Color.BLACK


def test_winner_tie_returns_none():
    b = Board()
    half = b.size * b.size // 2
    flat = [(r, c) for r in range(b.size) for c in range(b.size)]
    for r, c in flat[:half]:
        b[r, c] = Color.BLACK
    for r, c in flat[half:]:
        b[r, c] = Color.WHITE
    assert winner(b) is None
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_rules.py -v -k "score or terminal or winner"`

기대 결과: 6개 테스트가 import 에러로 실패.

- [ ] **Step 3: `score`, `is_terminal`, `winner` 구현**

`c:/Users/elec9/othello/othello/core/rules.py` 끝에 추가:
```python
def score(board: Board) -> tuple[int, int]:
    black = white = 0
    for _, _, c in board.cells():
        if c is Color.BLACK:
            black += 1
        elif c is Color.WHITE:
            white += 1
    return black, white


def is_terminal(board: Board) -> bool:
    return not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE)


def winner(board: Board) -> Color | None:
    b, w = score(board)
    if b > w:
        return Color.BLACK
    if w > b:
        return Color.WHITE
    return None
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_rules.py -v`

기대 결과: 15 passed total.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add score, is_terminal, winner"
```

---

## Task 7: GameState — `play` 와 `undo`

**파일:**
- 생성: `othello/othello/core/game.py`
- 생성: `othello/tests/test_game.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_game.py` 생성:
```python
import pytest
from othello.core.board import Color, Move
from othello.core.game import GameState


def test_initial_state_is_black_to_move():
    s = GameState()
    assert s.current is Color.BLACK
    assert s.history == []


def test_play_legal_move_advances_turn():
    s = GameState()
    s.play(Move(2, 3))
    assert s.current is Color.WHITE
    assert s.board[2, 3] is Color.BLACK
    assert s.board[3, 3] is Color.BLACK  # 뒤집힘
    assert len(s.history) == 1


def test_play_illegal_move_raises():
    s = GameState()
    with pytest.raises(ValueError):
        s.play(Move(0, 0))


def test_undo_restores_previous_state():
    s = GameState()
    snapshot_board = [[s.board[r, c] for c in range(s.board.size)] for r in range(s.board.size)]
    s.play(Move(2, 3))
    s.undo()
    assert s.current is Color.BLACK
    for r in range(s.board.size):
        for c in range(s.board.size):
            assert s.board[r, c] is snapshot_board[r][c]
    assert s.history == []


def test_undo_without_history_raises():
    s = GameState()
    with pytest.raises(IndexError):
        s.undo()


def test_play_undo_round_trip_two_moves():
    s = GameState()
    s.play(Move(2, 3))
    s.play(Move(2, 2))  # WHITE 응수
    assert s.current is Color.BLACK
    s.undo()
    assert s.current is Color.WHITE
    s.undo()
    assert s.current is Color.BLACK
    assert s.history == []


def test_score_delegates_to_rules():
    s = GameState()
    assert s.score() == (2, 2)
    s.play(Move(2, 3))
    assert s.score() == (4, 1)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_game.py -v`

기대 결과: 모두 `ModuleNotFoundError` 로 실패.

- [ ] **Step 3: GameState 구현 (auto-pass 제외)**

`c:/Users/elec9/othello/othello/core/game.py` 생성:
```python
from dataclasses import dataclass

from othello.core.board import Board, Color, Move, PASS
from othello.core.rules import (
    apply_move,
    is_terminal,
    legal_moves,
    score,
    winner,
)


@dataclass
class HistoryEntry:
    board_before: Board
    color_to_move: Color
    move: Move


class GameState:
    def __init__(self, size: int = 8):
        self.board: Board = Board(size)
        self.current: Color = Color.BLACK
        self.history: list[HistoryEntry] = []

    def legal_moves(self) -> list[Move]:
        return legal_moves(self.board, self.current)

    def play(self, move: Move) -> None:
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))
        self.board = apply_move(self.board, move, self.current)
        self.current = self.current.opponent()

    def undo(self) -> None:
        if not self.history:
            raise IndexError("No history to undo")
        entry = self.history.pop()
        self.board = entry.board_before
        self.current = entry.color_to_move

    def score(self) -> tuple[int, int]:
        return score(self.board)

    def winner(self) -> Color | None:
        return winner(self.board)

    def is_over(self) -> bool:
        return is_terminal(self.board)
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_game.py -v`

기대 결과: 7 passed.

- [ ] **Step 5: 커밋**

```bash
git add othello/core/game.py tests/test_game.py
git commit -m "feat(core): add GameState with play/undo/history"
```

---

## Task 8: GameState — Auto-Pass

**파일:**
- 수정: `othello/othello/core/game.py`
- 수정: `othello/tests/test_game.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_game.py` 끝에 추가:
```python
def _make_pass_position():
    """BLACK이 둔 직후 WHITE에게 합법수가 없는 보드를 구성합니다."""
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    s.board[0, 0] = Color.WHITE
    s.board[7, 7] = Color.BLACK
    s.board[7, 6] = Color.WHITE
    s.board[7, 5] = Color.BLACK
    s.current = Color.BLACK
    return s


def test_must_pass_detection():
    # 위 인공 보드는 사실 양쪽 모두 합법수가 없는 게임 종료 상태이므로
    # 실제 auto-pass 케이스는 다음 테스트에서 검증합니다.
    pass


def test_auto_pass_when_opponent_has_no_moves():
    """둔 후 상대에게 합법수가 없고 본인에게는 있을 때, 같은 색이 다시 둘 차례가 되며
    PASS 가 history 에 기록되어야 합니다."""
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    # 인공 보드: BLACK 이 (1,1)에 두면 (2,2)의 WHITE 가 뒤집힘.
    # 그 결과 WHITE 에게 합법수가 없고, BLACK 에게는 또 다른 합법수가 남도록 구성.
    s.board[0, 0] = Color.WHITE
    s.board[0, 1] = Color.BLACK
    s.board[0, 2] = Color.WHITE
    s.board[0, 3] = Color.BLACK
    s.board[2, 2] = Color.WHITE
    s.board[3, 3] = Color.BLACK
    s.current = Color.BLACK

    # 사전 검증: 현재 WHITE 에게 합법수 없음
    from othello.core.rules import legal_moves
    assert legal_moves(s.board, Color.WHITE) == []

    s.play(Move(1, 1))
    # WHITE 가 자동 패스되어 다시 BLACK 의 차례여야 합니다.
    assert s.current is Color.BLACK
    # history 는 두 항목(실제 수 + auto-pass)을 가져야 합니다.
    assert len(s.history) == 2
    assert s.history[-1].move.is_pass


def test_undo_after_auto_pass_pops_both_entries():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    s.board[0, 0] = Color.WHITE
    s.board[0, 1] = Color.BLACK
    s.board[0, 2] = Color.WHITE
    s.board[0, 3] = Color.BLACK
    s.board[2, 2] = Color.WHITE
    s.board[3, 3] = Color.BLACK
    s.current = Color.BLACK

    s.play(Move(1, 1))
    assert len(s.history) == 2
    s.undo()
    assert s.current is Color.BLACK
    assert s.history == []
    assert s.board[1, 1] is Color.EMPTY
    assert s.board[2, 2] is Color.WHITE


def test_is_over_when_neither_side_has_moves():
    s = GameState()
    # 보드를 BLACK 으로 가득 채우면 양쪽 모두 합법수 없음
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    assert s.is_over() is True
```

(첫 번째 `test_must_pass_detection` 은 의도적으로 비어 있는 문서용 자리표시자입니다 — pytest 는 빈 함수 body 도 통과로 처리합니다.)

- [ ] **Step 2: auto-pass 테스트 실패 확인**

실행: `pytest tests/test_game.py -v -k auto_pass`

기대 결과: `test_auto_pass_when_opponent_has_no_moves` 와 `test_undo_after_auto_pass_pops_both_entries` 가 `play` 의 auto-pass 미구현 때문에 실패.

- [ ] **Step 3: auto-pass 구현**

`c:/Users/elec9/othello/othello/core/game.py` 의 `play` / `undo` 메서드를 다음으로 교체:
```python
    def must_pass(self) -> bool:
        return (
            not legal_moves(self.board, self.current)
            and bool(legal_moves(self.board, self.current.opponent()))
        )

    def play(self, move: Move) -> None:
        if move.is_pass:
            if not self.must_pass():
                raise ValueError("PASS is only legal when the current player has no moves")
            self.history.append(HistoryEntry(self.board.copy(), self.current, move))
            self.current = self.current.opponent()
            return
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))
        self.board = apply_move(self.board, move, self.current)
        self.current = self.current.opponent()
        # Auto-pass: 상대가 합법수가 없고 본인에게는 합법수가 있을 때
        if (
            not legal_moves(self.board, self.current)
            and legal_moves(self.board, self.current.opponent())
        ):
            self.history.append(HistoryEntry(self.board.copy(), self.current, PASS))
            self.current = self.current.opponent()

    def undo(self) -> None:
        if not self.history:
            raise IndexError("No history to undo")
        entry = self.history.pop()
        # 마지막 항목이 auto-pass 였다면 그 직전의 실제 수까지 함께 되돌립니다.
        while entry.move.is_pass and self.history:
            entry = self.history.pop()
        self.board = entry.board_before
        self.current = entry.color_to_move
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_game.py -v`

기대 결과: 11 passed (placeholder 포함).

- [ ] **Step 5: 커밋**

```bash
git add othello/core/game.py tests/test_game.py
git commit -m "feat(core): add auto-pass and must_pass to GameState"
```

---

## Task 9: AI — Strategy ABC 와 RandomAI

**파일:**
- 생성: `othello/othello/ai/__init__.py` (빈 파일)
- 생성: `othello/othello/ai/base.py`
- 생성: `othello/othello/ai/random_ai.py`
- 생성: `othello/tests/test_ai.py`

- [ ] **Step 1: 빈 패키지 init 생성**

`c:/Users/elec9/othello/othello/ai/__init__.py` 를 빈 파일로 생성.

- [ ] **Step 2: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_ai.py` 생성:
```python
import pytest
from othello.core.game import GameState
from othello.core.board import Color
from othello.ai.base import Strategy
from othello.ai.random_ai import RandomAI


def test_random_ai_returns_legal_move():
    s = GameState()
    ai = RandomAI(seed=0)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_random_ai_is_seeded_deterministic():
    s = GameState()
    ai1 = RandomAI(seed=42)
    ai2 = RandomAI(seed=42)
    assert ai1.select_move(s) == ai2.select_move(s)


def test_random_ai_raises_when_no_legal_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = RandomAI()
    with pytest.raises(ValueError):
        ai.select_move(s)


def test_strategy_is_abstract():
    with pytest.raises(TypeError):
        Strategy()  # ABC 는 직접 인스턴스화 불가
```

- [ ] **Step 3: 테스트 실패 확인**

실행: `pytest tests/test_ai.py -v`

기대 결과: 모두 `ModuleNotFoundError` 로 실패.

- [ ] **Step 4: Strategy 와 RandomAI 구현**

`c:/Users/elec9/othello/othello/ai/base.py` 생성:
```python
from abc import ABC, abstractmethod

from othello.core.board import Move
from othello.core.game import GameState


class Strategy(ABC):
    name: str = ""

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """`state.legal_moves()`에서 합법수 하나를 반환.
        합법수가 없으면 ValueError 를 발생시켜야 합니다."""
```

`c:/Users/elec9/othello/othello/ai/random_ai.py` 생성:
```python
import random

from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState


class RandomAI(Strategy):
    name = "Random"

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("RandomAI: no legal moves available")
        return self._rng.choice(moves)
```

- [ ] **Step 5: 테스트 통과 확인**

실행: `pytest tests/test_ai.py -v`

기대 결과: 4 passed.

- [ ] **Step 6: 커밋**

```bash
git add othello/ai/__init__.py othello/ai/base.py othello/ai/random_ai.py tests/test_ai.py
git commit -m "feat(ai): add Strategy ABC and RandomAI"
```

---

## Task 10: AI — GreedyAI

**파일:**
- 생성: `othello/othello/ai/greedy.py`
- 수정: `othello/tests/test_ai.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_ai.py` 끝에 추가:
```python
from othello.ai.greedy import GreedyAI
from othello.core.rules import flips_for


def test_greedy_picks_max_flips():
    s = GameState()
    ai = GreedyAI()
    move = ai.select_move(s)
    chosen = len(flips_for(s.board, move, s.current))
    for m in s.legal_moves():
        assert chosen >= len(flips_for(s.board, m, s.current))


def test_greedy_returns_legal_move():
    s = GameState()
    ai = GreedyAI()
    assert ai.select_move(s) in s.legal_moves()
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_ai.py -v -k greedy`

기대 결과: 2개 실패.

- [ ] **Step 3: GreedyAI 구현**

`c:/Users/elec9/othello/othello/ai/greedy.py` 생성:
```python
from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState
from othello.core.rules import flips_for


class GreedyAI(Strategy):
    name = "Greedy"

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("GreedyAI: no legal moves available")
        return max(moves, key=lambda m: len(flips_for(state.board, m, state.current)))
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_ai.py -v`

기대 결과: 6 passed total.

- [ ] **Step 5: 커밋**

```bash
git add othello/ai/greedy.py tests/test_ai.py
git commit -m "feat(ai): add GreedyAI"
```

---

## Task 11: AI — 평가 함수

**파일:**
- 생성: `othello/othello/ai/evaluation.py`
- 생성: `othello/tests/test_evaluation.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_evaluation.py` 생성:
```python
from othello.core.board import Board, Color
from othello.ai.evaluation import evaluate


def test_evaluate_initial_position_is_neutral():
    b = Board()
    # 대칭 상태이므로 평가값은 0
    assert evaluate(b, Color.BLACK) == 0


def test_evaluate_corner_value_is_high_for_owner_8x8():
    b = Board()
    b[0, 0] = Color.BLACK
    val_black = evaluate(b, Color.BLACK)
    val_white = evaluate(b, Color.WHITE)
    assert val_black > 0
    assert val_white < 0
    # 부호 대칭
    assert val_black == -val_white


def test_evaluate_endgame_uses_score_difference():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    val = evaluate(b, Color.BLACK)
    assert val > 1000  # 종료 상태의 큰 평가값


def test_evaluate_works_for_6x6_and_10x10():
    b6 = Board(size=6)
    b10 = Board(size=10)
    assert isinstance(evaluate(b6, Color.BLACK), int)
    assert isinstance(evaluate(b10, Color.BLACK), int)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_evaluation.py -v`

기대 결과: 모두 `ModuleNotFoundError`.

- [ ] **Step 3: 평가 함수 구현**

`c:/Users/elec9/othello/othello/ai/evaluation.py` 생성:
```python
from othello.core.board import Board, Color
from othello.core.rules import legal_moves, score

WEIGHTS_8X8: list[list[int]] = [
    [100, -25,  10,   5,   5,  10, -25, 100],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [100, -25,  10,   5,   5,  10, -25, 100],
]


def _generic_value(size: int, r: int, c: int) -> int:
    is_corner = r in (0, size - 1) and c in (0, size - 1)
    is_edge = r in (0, size - 1) or c in (0, size - 1)
    if is_corner:
        return 30
    if is_edge:
        return 5
    return 1


def _terminal_eval(board: Board, color: Color) -> int:
    b, w = score(board)
    diff = b - w
    sign = 1 if color is Color.BLACK else -1
    return sign * diff * 10000


def evaluate(board: Board, color: Color) -> int:
    # 종료: 양쪽 모두 합법수 없음
    if not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE):
        return _terminal_eval(board, color)

    use_weights = (board.size == 8)
    total = 0
    for r, c, cell in board.cells():
        if cell is Color.EMPTY:
            continue
        v = WEIGHTS_8X8[r][c] if use_weights else _generic_value(board.size, r, c)
        if cell is color:
            total += v
        else:
            total -= v
    return total
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_evaluation.py -v`

기대 결과: 4 passed.

- [ ] **Step 5: 커밋**

```bash
git add othello/ai/evaluation.py tests/test_evaluation.py
git commit -m "feat(ai): add positional evaluation function"
```

---

## Task 12: AI — MinimaxAI

**파일:**
- 생성: `othello/othello/ai/minimax.py`
- 수정: `othello/tests/test_ai.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_ai.py` 끝에 추가:
```python
from othello.ai.minimax import MinimaxAI


def test_minimax_returns_legal_move():
    s = GameState()
    ai = MinimaxAI(depth=2)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_depth_1_picks_best_immediate():
    s = GameState()
    ai = MinimaxAI(depth=1)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_minimax_raises_with_no_legal_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = MinimaxAI(depth=2)
    with pytest.raises(ValueError):
        ai.select_move(s)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_ai.py -v -k minimax`

기대 결과: 3개 실패.

- [ ] **Step 3: MinimaxAI 구현**

`c:/Users/elec9/othello/othello/ai/minimax.py` 생성:
```python
from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class MinimaxAI(Strategy):
    name = "Minimax"

    def __init__(self, depth: int = 3):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("MinimaxAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(new_board, root_color.opponent(), self.depth - 1, root_color)
            if val > best_val:
                best_val = val
                best_move = m
        return best_move

    def _search(self, board: Board, to_move: Color, depth: int, root_color: Color) -> float:
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, root_color)
        if to_move is root_color:
            best = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v > best:
                    best = v
            return best
        else:
            best = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v < best:
                    best = v
            return best
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_ai.py -v`

기대 결과: 9 passed total.

- [ ] **Step 5: 커밋**

```bash
git add othello/ai/minimax.py tests/test_ai.py
git commit -m "feat(ai): add MinimaxAI with depth-limited search"
```

---

## Task 13: AI — AlphaBetaAI + Minimax 동치 테스트

**파일:**
- 생성: `othello/othello/ai/alphabeta.py`
- 수정: `othello/tests/test_ai.py`

- [ ] **Step 1: 실패하는 테스트 추가**

`c:/Users/elec9/othello/tests/test_ai.py` 끝에 추가:
```python
from othello.ai.alphabeta import AlphaBetaAI


def test_alphabeta_returns_legal_move():
    s = GameState()
    ai = AlphaBetaAI(depth=3)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_and_alphabeta_agree_on_initial_position():
    """같은 깊이에서 alpha-beta 가지치기는 선택 결과를 바꾸면 안 됩니다."""
    s = GameState()
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)


def test_minimax_and_alphabeta_agree_after_few_plays():
    s = GameState()
    s.play(s.legal_moves()[0])
    s.play(s.legal_moves()[0])
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_ai.py -v -k alphabeta`

기대 결과: 3개 실패.

- [ ] **Step 3: AlphaBetaAI 구현**

`c:/Users/elec9/othello/othello/ai/alphabeta.py` 생성:
```python
from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class AlphaBetaAI(Strategy):
    name = "Alpha-Beta"

    def __init__(self, depth: int = 5):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("AlphaBetaAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        alpha, beta = -INF, INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(
                new_board, root_color.opponent(), self.depth - 1, alpha, beta, root_color
            )
            if val > best_val:
                best_val = val
                best_move = m
            alpha = max(alpha, val)
        return best_move

    def _search(
        self,
        board: Board,
        to_move: Color,
        depth: int,
        alpha: float,
        beta: float,
        root_color: Color,
    ) -> float:
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, alpha, beta, root_color)
        if to_move is root_color:
            value = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v > value:
                    value = v
                if value > alpha:
                    alpha = value
                if alpha >= beta:
                    break
            return value
        else:
            value = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v < value:
                    value = v
                if value < beta:
                    beta = value
                if alpha >= beta:
                    break
            return value
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_ai.py -v`

기대 결과: 12 passed total.

- [ ] **Step 5: 커밋**

```bash
git add othello/ai/alphabeta.py tests/test_ai.py
git commit -m "feat(ai): add AlphaBetaAI with parity test vs Minimax"
```

---

## Task 14: 영속화 — history 재생 기반 save/load

**파일:**
- 생성: `othello/othello/persistence.py`
- 생성: `othello/tests/test_persistence.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`c:/Users/elec9/othello/tests/test_persistence.py` 생성:
```python
import pytest
from pathlib import Path

from othello.core.board import Color, Move
from othello.core.game import GameState
from othello.persistence import save_game, load_game


def test_round_trip_empty_game(tmp_path: Path):
    s = GameState(size=8)
    p = tmp_path / "g.json"
    save_game(s, {"mode": "two_player"}, p)
    s2, info = load_game(p)
    assert s2.board.size == 8
    assert s2.current is Color.BLACK
    assert info == {"mode": "two_player"}


def test_round_trip_after_moves(tmp_path: Path):
    s = GameState(size=8)
    s.play(Move(2, 3))
    s.play(Move(2, 2))
    p = tmp_path / "g.json"
    save_game(s, {"mode": "vs_ai", "ai_difficulty": "minimax"}, p)
    s2, info = load_game(p)
    assert s2.current is s.current
    for r in range(8):
        for c in range(8):
            assert s2.board[r, c] is s.board[r, c]
    assert info["ai_difficulty"] == "minimax"


def test_load_rejects_unknown_version(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text('{"version": 999, "size": 8, "current": "BLACK", "history": []}')
    with pytest.raises(ValueError):
        load_game(p)


def test_load_rejects_invalid_replay(tmp_path: Path):
    p = tmp_path / "bad.json"
    # (0,0)은 시작 상태에서 불법수
    p.write_text(
        '{"version": 1, "size": 8, "current": "BLACK", '
        '"mode_info": {}, "history": [{"row": 0, "col": 0, "color": "BLACK"}]}'
    )
    with pytest.raises(ValueError):
        load_game(p)
```

- [ ] **Step 2: 테스트 실패 확인**

실행: `pytest tests/test_persistence.py -v`

기대 결과: 모두 `ModuleNotFoundError`.

- [ ] **Step 3: 영속화 구현**

`c:/Users/elec9/othello/othello/persistence.py` 생성:
```python
import json
from pathlib import Path
from typing import Any

from othello.core.board import Color, Move
from othello.core.game import GameState

VERSION = 1


def save_game(state: GameState, mode_info: dict[str, Any], path: Path | str) -> None:
    data = {
        "version": VERSION,
        "size": state.board.size,
        "current": state.current.name,
        "mode_info": mode_info,
        "history": [
            {"row": e.move.row, "col": e.move.col, "color": e.color_to_move.name}
            for e in state.history
        ],
    }
    Path(path).write_text(json.dumps(data, indent=2))


def load_game(path: Path | str) -> tuple[GameState, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    if data.get("version") != VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')!r}")
    size = data["size"]
    state = GameState(size=size)
    for entry in data.get("history", []):
        move = Move(entry["row"], entry["col"])
        if move.is_pass:
            # auto-pass 항목은 play() 가 자동 생성
            continue
        expected_color = Color[entry["color"]]
        if state.current is not expected_color:
            raise ValueError(
                f"Replay mismatch at {move}: expected {state.current.name}, "
                f"saved as {expected_color.name}"
            )
        state.play(move)
    return state, data.get("mode_info", {})
```

- [ ] **Step 4: 테스트 통과 확인**

실행: `pytest tests/test_persistence.py -v`

기대 결과: 4 passed.

- [ ] **Step 5: 전체 테스트 실행**

실행: `pytest -v`

기대 결과: 모든 테스트 통과 (~40개). 실패가 있다면 다음으로 넘어가기 전에 수정 — UI 작업은 깨끗한 코어를 전제로 합니다.

- [ ] **Step 6: 커밋**

```bash
git add othello/persistence.py tests/test_persistence.py
git commit -m "feat: add JSON save/load via history replay"
```

---

## Task 15: UI — 앱 셸 + main.py

**파일:**
- 생성: `othello/othello/ui/__init__.py` (빈 파일)
- 생성: `othello/othello/ui/app.py`
- 생성: `othello/main.py`

UI 작업은 스펙 §10 에 따라 자동 테스트가 없습니다. 각 Task 의 마지막 단계는 수동 스모크 테스트입니다.

- [ ] **Step 1: 빈 패키지 init 생성**

`c:/Users/elec9/othello/othello/ui/__init__.py` 를 빈 파일로 생성.

- [ ] **Step 2: 앱 셸 구현**

`c:/Users/elec9/othello/othello/ui/app.py` 생성:
```python
import tkinter as tk
from typing import Any


class OthelloApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Othello")
        self.root.geometry("800x600")
        self.current_screen: tk.Frame | None = None
        self.show_menu()

    def show_menu(self) -> None:
        from othello.ui.menu_screen import MenuScreen
        self._switch(MenuScreen(self.root, self))

    def show_game(self, config: dict[str, Any]) -> None:
        from othello.ui.game_screen import GameScreen
        self._switch(GameScreen(self.root, self, config))

    def _switch(self, frame: tk.Frame) -> None:
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = frame
        frame.pack(fill="both", expand=True)
```

- [ ] **Step 3: main.py 구현**

`c:/Users/elec9/othello/main.py` 생성:
```python
import tkinter as tk

from othello.ui.app import OthelloApp


def main() -> None:
    root = tk.Tk()
    OthelloApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: import 새너티 체크**

실행: `python -c "from othello.ui.app import OthelloApp; print('ok')"`

기대 결과: `ok` (import 에러 없음). 실제로 실행하면 `MenuScreen`, `GameScreen` 이 아직 없으니 런타임 에러가 나지만 정상 — 다음 Task 에서 채웁니다.

- [ ] **Step 5: 커밋**

```bash
git add othello/ui/__init__.py othello/ui/app.py main.py
git commit -m "feat(ui): add Tk app shell and main entry point"
```

---

## Task 16: UI — 메뉴 화면

**파일:**
- 생성: `othello/othello/ui/menu_screen.py`
- 생성: `othello/othello/ui/game_screen.py` (스텁, Task 18 에서 교체)

- [ ] **Step 1: GameScreen 스텁 생성**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 생성:
```python
import tkinter as tk
from tkinter import ttk
from typing import Any


class GameScreen(tk.Frame):
    """스텁: Task 18 에서 완전 교체됩니다."""

    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.config_data = config
        ttk.Label(self, text=f"Game stub. Config: {config}").pack(padx=20, pady=20)
        ttk.Button(self, text="Back to Menu", command=app.show_menu).pack(pady=10)
```

- [ ] **Step 2: MenuScreen 구현**

`c:/Users/elec9/othello/othello/ui/menu_screen.py` 생성:
```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any


class MenuScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app):
        super().__init__(root)
        self.app = app

        ttk.Label(self, text="Othello", font=("Helvetica", 32, "bold")).pack(pady=20)

        # 모드 선택
        self.mode_var = tk.StringVar(value="two_player")
        mode_frame = ttk.LabelFrame(self, text="Mode")
        mode_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(
            mode_frame, text="2 Player", variable=self.mode_var, value="two_player",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)
        ttk.Radiobutton(
            mode_frame, text="vs AI", variable=self.mode_var, value="vs_ai",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)

        # AI 난이도
        self.ai_var = tk.StringVar(value="alphabeta")
        ai_frame = ttk.LabelFrame(self, text="AI Difficulty")
        ai_frame.pack(padx=20, pady=10, fill="x")
        for label, val in [
            ("Random", "random"), ("Greedy", "greedy"),
            ("Minimax", "minimax"), ("Alpha-Beta", "alphabeta"),
        ]:
            ttk.Radiobutton(ai_frame, text=label, variable=self.ai_var, value=val).pack(anchor="w", padx=10)
        self.ai_frame = ai_frame

        # 사용자 색상
        self.color_var = tk.StringVar(value="BLACK")
        color_frame = ttk.LabelFrame(self, text="Human Color")
        color_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(color_frame, text="Black (first)", variable=self.color_var, value="BLACK").pack(anchor="w", padx=10)
        ttk.Radiobutton(color_frame, text="White (second)", variable=self.color_var, value="WHITE").pack(anchor="w", padx=10)
        self.color_frame = color_frame

        # 보드 크기
        self.size_var = tk.IntVar(value=8)
        size_frame = ttk.LabelFrame(self, text="Board Size")
        size_frame.pack(padx=20, pady=10, fill="x")
        for s in (6, 8, 10):
            ttk.Radiobutton(size_frame, text=f"{s}×{s}", variable=self.size_var, value=s).pack(anchor="w", padx=10)

        # 버튼
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Start", command=self._start).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Saved Game", command=self._load).pack(side="left", padx=5)

        self._refresh_enabled()

    def _refresh_enabled(self) -> None:
        state = "normal" if self.mode_var.get() == "vs_ai" else "disabled"
        for child in self.ai_frame.winfo_children():
            child.configure(state=state)
        for child in self.color_frame.winfo_children():
            child.configure(state=state)

    def _start(self) -> None:
        config: dict[str, Any] = {
            "mode": self.mode_var.get(),
            "size": self.size_var.get(),
        }
        if config["mode"] == "vs_ai":
            config["ai_difficulty"] = self.ai_var.get()
            config["human_color"] = self.color_var.get()
        self.app.show_game(config)

    def _load(self) -> None:
        path = filedialog.askopenfilename(
            title="Load saved game",
            filetypes=[("JSON saves", "*.json"), ("All files", "*.*")],
            initialdir="savegames",
        )
        if not path:
            return
        try:
            from othello.persistence import load_game
            state, info = load_game(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Load failed", f"Could not load save:\n{exc}")
            return
        config = dict(info)
        config["size"] = state.board.size
        config["_loaded_state"] = state
        self.app.show_game(config)
```

- [ ] **Step 3: 수동 스모크 테스트**

실행: `python main.py`

기대 동작:
- 제목이 "Othello"인 창이 열립니다.
- Mode / AI Difficulty / Human Color / Board Size / Start·Load 버튼이 보입니다.
- "2 Player" 선택 시 AI Difficulty 와 Human Color 라디오가 비활성화, "vs AI" 선택 시 활성화.
- Start 클릭 시 GameScreen 스텁이 나타나며 선택한 config 가 표시되고, "Back to Menu" 로 돌아옵니다.
- "Load Saved Game" 에서 파일 선택을 취소하면 아무 일도 일어나지 않으며, 잘못된 파일을 선택하면 에러 다이얼로그가 뜹니다.

확인 후 창을 닫습니다.

- [ ] **Step 4: 커밋**

```bash
git add othello/ui/menu_screen.py othello/ui/game_screen.py
git commit -m "feat(ui): add menu screen with mode/AI/size selection"
```

---

## Task 17: UI — Board View (렌더링 + 클릭 + 합법수 표시)

**파일:**
- 생성: `othello/othello/ui/board_view.py`

Board view 는 셀 / 돌 / 합법수 점을 그리는 `Canvas` 위젯이며, `on_click(row, col)` 콜백을 외부에 노출합니다.

- [ ] **Step 1: BoardView 구현**

`c:/Users/elec9/othello/othello/ui/board_view.py` 생성:
```python
import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

CELL_PX = 60
PAD = 10
LINE_COLOR = "#2c3e50"
BOARD_COLOR = "#0e7c3a"
HINT_COLOR = "#ffd54f"


class BoardView(tk.Frame):
    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self, width=canvas_px, height=canvas_px,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)
        self._stones: dict[tuple[int, int], int] = {}
        self._hints: list[int] = []
        self._draw_grid()

    def _draw_grid(self) -> None:
        for i in range(self.size + 1):
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = (CELL_PX / 2 - 4) * scale
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR, outline="",
        )

    def _handle_click(self, event: tk.Event) -> None:
        if self.is_animating:
            return
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))
```

- [ ] **Step 2: GameScreen 스텁에 BoardView 연결 (스모크 테스트용)**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 를 다음으로 교체:
```python
import tkinter as tk
from tkinter import ttk
from typing import Any

from othello.core.game import GameState
from othello.ui.board_view import BoardView


class GameScreen(tk.Frame):
    """스모크 테스트용: 보드를 그리고 클릭을 출력합니다. Task 18 에서 교체."""

    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.state = config.get("_loaded_state") or GameState(size=config.get("size", 8))

        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)
        ttk.Button(side, text="Back to Menu", command=app.show_menu).pack(pady=5)

        self._refresh()

    def _on_click(self, row: int, col: int) -> None:
        print(f"clicked ({row}, {col})")  # 진단용

    def _refresh(self) -> None:
        self.board_view.render(self.state.board, hints=self.state.legal_moves())
```

- [ ] **Step 3: 수동 스모크 테스트**

실행: `python main.py`

기대 동작:
- "2 Player" + 8×8 + Start.
- 격자가 그려진 초록 보드 위 중앙에 4개의 돌이 표시됩니다 (검정 2 + 흰색 2).
- BLACK 의 합법수 위치 4곳에 작은 노란 점이 표시됩니다.
- 셀을 클릭하면 터미널에 `clicked (r, c)` 가 출력됩니다 — 에러 없음.
- 6×6, 10×10 크기도 정상적으로 렌더링.

확인 후 종료.

- [ ] **Step 4: 커밋**

```bash
git add othello/ui/board_view.py othello/ui/game_screen.py
git commit -m "feat(ui): add BoardView with rendering, hints, and clicks"
```

---

## Task 18: UI — Game Screen (턴/점수/히스토리/Undo/Hint/Save)

Task 17 의 스텁을 컨트롤러 풀버전으로 교체합니다. AI 연동과 애니메이션은 다음 Task 에서 추가합니다.

**파일:**
- 수정: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: GameScreen 풀버전 구현**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 를 다음으로 교체:
```python
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from othello.core.board import Color, Move
from othello.core.game import GameState
from othello.persistence import save_game
from othello.ui.board_view import BoardView


def _move_label(m: Move, size: int) -> str:
    if m.is_pass:
        return "pass"
    return f"{chr(ord('a') + m.col)}{m.row + 1}"


class GameScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.config_data = dict(config)
        loaded = self.config_data.pop("_loaded_state", None)
        size = self.config_data.get("size", 8)
        self.state: GameState = loaded if loaded is not None else GameState(size=size)

        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)

        self.turn_label = ttk.Label(side, text="", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(anchor="w", pady=5)
        self.score_label = ttk.Label(side, text="", font=("Helvetica", 12))
        self.score_label.pack(anchor="w", pady=5)

        ttk.Button(side, text="Undo", command=self._undo).pack(fill="x", pady=2)
        ttk.Button(side, text="Hint", command=self._hint).pack(fill="x", pady=2)
        ttk.Button(side, text="Save", command=self._save).pack(fill="x", pady=2)
        ttk.Button(side, text="Menu", command=app.show_menu).pack(fill="x", pady=2)

        ttk.Label(side, text="History:").pack(anchor="w", pady=(10, 2))
        self.history_text = tk.Text(side, width=24, height=20, state="disabled")
        self.history_text.pack(fill="y", expand=True)

        self._hint_move: Move | None = None
        self._refresh()

    # --- 이벤트 핸들러 ---

    def _on_click(self, row: int, col: int) -> None:
        if self.board_view.is_animating:
            return
        move = Move(row, col)
        if move not in self.state.legal_moves():
            return  # 스펙 §11: 불법 클릭은 조용히 무시
        self._play(move)

    def _play(self, move: Move) -> None:
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None
        self._refresh()
        if self.state.is_over():
            self._announce_winner()

    def _undo(self) -> None:
        if not self.state.history:
            return
        self.state.undo()
        self._hint_move = None
        self._refresh()

    def _hint(self) -> None:
        moves = self.state.legal_moves()
        if not moves:
            return
        # 힌트는 항상 강한 AI 사용 (대전 상대 설정과 무관)
        from othello.ai.alphabeta import AlphaBetaAI
        self._hint_move = AlphaBetaAI(depth=3).select_move(self.state)
        self._refresh()

    def _save(self) -> None:
        Path("savegames").mkdir(exist_ok=True)
        default = f"savegames/othello-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title="Save game",
            defaultextension=".json",
            filetypes=[("JSON saves", "*.json")],
            initialfile=Path(default).name,
            initialdir="savegames",
        )
        if not path:
            return
        try:
            save_game(self.state, self.config_data, path)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))

    # --- 렌더링 ---

    def _refresh(self) -> None:
        legal = self.state.legal_moves()
        hints = legal if not self._hint_move else [self._hint_move]
        self.board_view.render(self.state.board, hints=hints)
        self._update_status()
        self._update_history()

    def _update_status(self) -> None:
        bullet = "●" if self.state.current is Color.BLACK else "○"
        self.turn_label.config(text=f"Turn: {bullet} {self.state.current.name}")
        b, w = self.state.score()
        self.score_label.config(text=f"Score:  ●{b}   ○{w}")

    def _update_history(self) -> None:
        size = self.state.board.size
        items = []
        move_num = 1
        for entry in self.state.history:
            label = _move_label(entry.move, size)
            color = "B" if entry.color_to_move is Color.BLACK else "W"
            items.append(f"{move_num}. {color} {label}")
            move_num += 1
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(items))
        self.history_text.config(state="disabled")

    def _announce_winner(self) -> None:
        w = self.state.winner()
        b, wh = self.state.score()
        if w is None:
            msg = f"Tie!  ●{b}   ○{wh}"
        else:
            msg = f"{w.name} wins!  ●{b}   ○{wh}"
        messagebox.showinfo("Game over", msg)
```

- [ ] **Step 2: 수동 스모크 테스트**

실행: `python main.py`

기대 동작:
- 2P 8×8 시작.
- 턴 라벨 "Turn: ● BLACK", 점수 "●2 ○2".
- 합법수 4곳에 노란 힌트 점.
- 합법수 클릭 시 돌이 놓이고 뒤집히며, 턴이 WHITE 로 바뀌고 점수가 갱신, 히스토리에 기록.
- 불법 클릭은 조용히 무시.
- "Undo" 로 직전 수 되돌리기.
- "Hint" 누르면 합법수 점들이 사라지고 추천 위치 한 곳에만 노란 점이 표시. 다시 두면 힌트 해제.
- "Save" → 파일명 입력 → `savegames/` 에 JSON 저장.
- 메뉴 → Load Saved Game 으로 그 파일을 불러오면 상태 복원.
- 작은 보드(6×6)에서 게임을 끝까지 진행하면 "Game over" 다이얼로그 표시.

확인 후 종료.

- [ ] **Step 3: 커밋**

```bash
git add othello/ui/game_screen.py
git commit -m "feat(ui): add full game screen with undo, hint, save, history"
```

---

## Task 19: UI — 애니메이션

`BoardView` 에 돌 배치/뒤집기 애니메이션을 추가합니다.

**파일:**
- 수정: `othello/othello/ui/board_view.py`
- 수정: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: BoardView 애니메이션 구현**

`c:/Users/elec9/othello/othello/ui/board_view.py` 를 다음으로 교체:
```python
import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

CELL_PX = 60
PAD = 10
LINE_COLOR = "#2c3e50"
BOARD_COLOR = "#0e7c3a"
HINT_COLOR = "#ffd54f"

PLACE_MS = 150
FLIP_MS = 200
FLIP_STAGGER_MS = 30
ANIM_FPS = 60


class BoardView(tk.Frame):
    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self, width=canvas_px, height=canvas_px,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)
        self._stones: dict[tuple[int, int], int] = {}
        self._hints: list[int] = []
        self._draw_grid()

    def _draw_grid(self) -> None:
        for i in range(self.size + 1):
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    # --- 정적 렌더링 ---

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    # --- 애니메이션 렌더링 ---

    def animate_move(
        self,
        new_board: Board,
        placed: Move,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        """`placed` 위치 돌 배치와 `flipped` 뒤집기를 애니메이션으로 표시한 뒤 `on_done` 호출.
        애니메이션 중에는 `is_animating` 이 True 입니다."""
        self.is_animating = True
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        placed_color = new_board[placed.row, placed.col]

        steps = max(1, int(PLACE_MS * ANIM_FPS / 1000))
        self._scale_in(placed.row, placed.col, placed_color, steps,
                       on_done=lambda: self._do_flips(new_board, flipped, on_done))

    def _scale_in(self, r: int, c: int, color: Color, steps: int, on_done: Callable[[], None]) -> None:
        if (r, c) in self._stones:
            self.canvas.delete(self._stones.pop((r, c)))
        delay = max(1, PLACE_MS // steps)

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            scale = (i + 1) / steps
            self._stones[(r, c)] = self._draw_stone(r, c, color, scale=scale)
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                on_done()

        step(0)

    def _do_flips(
        self,
        new_board: Board,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        if not flipped:
            self.is_animating = False
            on_done()
            return
        remaining = {"count": len(flipped)}

        def finish_one() -> None:
            remaining["count"] -= 1
            if remaining["count"] == 0:
                self.is_animating = False
                on_done()

        for i, (r, c) in enumerate(flipped):
            new_color = new_board[r, c]
            self.canvas.after(
                i * FLIP_STAGGER_MS,
                lambda r=r, c=c, nc=new_color: self._flip_one(r, c, nc, finish_one),
            )

    def _flip_one(self, r: int, c: int, new_color: Color, on_done: Callable[[], None]) -> None:
        steps = max(2, int(FLIP_MS * ANIM_FPS / 1000))
        delay = max(1, FLIP_MS // steps)
        old_color = new_color.opponent()

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            half = steps // 2
            if i < half:
                width_scale = 1 - (i / half)
                self._stones[(r, c)] = self._draw_oval_scaled(r, c, old_color, x_scale=max(0.05, width_scale))
            else:
                width_scale = (i - half + 1) / max(1, steps - half)
                self._stones[(r, c)] = self._draw_oval_scaled(r, c, new_color, x_scale=max(0.05, width_scale))
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                self.canvas.delete(self._stones[(r, c)])
                self._stones[(r, c)] = self._draw_stone(r, c, new_color)
                on_done()

        step(0)

    # --- 그리기 헬퍼 ---

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = (CELL_PX / 2 - 4) * scale
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_oval_scaled(self, r: int, c: int, color: Color, x_scale: float) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        rx = (CELL_PX / 2 - 4) * x_scale
        ry = CELL_PX / 2 - 4
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - rx, y - ry, x + rx, y + ry,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR, outline="",
        )

    def _handle_click(self, event: tk.Event) -> None:
        if self.is_animating:
            return
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))
```

- [ ] **Step 2: GameScreen._play 에서 애니메이션 사용**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 의 `_play` 메서드를 다음으로 교체:

기존:
```python
    def _play(self, move: Move) -> None:
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None
        self._refresh()
        if self.state.is_over():
            self._announce_winner()
```

변경 후:
```python
    def _play(self, move: Move) -> None:
        from othello.core.rules import flips_for
        flips = flips_for(self.state.board, move, self.state.current)
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None

        def after_anim() -> None:
            self._refresh()
            if self.state.is_over():
                self._announce_winner()

        self.board_view.animate_move(self.state.board, move, flips, after_anim)
        self._update_status()
        self._update_history()
```

원하면 import 도 파일 상단으로 옮길 수 있습니다 (`from othello.core.rules import flips_for`).

- [ ] **Step 3: 수동 스모크 테스트**

`python main.py` 실행. 2P 8×8 시작.

기대 동작:
- 합법수 클릭 시 새 돌이 작은 점에서 풀 사이즈로 (~150ms) 확대됨.
- 뒤집힌 돌들은 가로로 잠깐 줄어들었다가 새 색으로 다시 펴지며, 돌 사이에 약간의 시차.
- 애니메이션 동안 추가 클릭은 무시됨.
- 애니메이션 종료 후 다음 플레이어의 합법수 점이 다시 표시됨.

확인 후 종료.

- [ ] **Step 4: 커밋**

```bash
git add othello/ui/board_view.py othello/ui/game_screen.py
git commit -m "feat(ui): add place and flip animations"
```

---

## Task 20: UI — 사운드

**파일:**
- 생성: `othello/othello/ui/sound.py`
- 수정: `othello/othello/ui/game_screen.py`

래퍼는 파일 누락이나 오디오 실패 시에도 게임을 절대 종료시키지 않아야 합니다 (스펙 §8.6, §11).

- [ ] **Step 1: 사운드 래퍼 구현**

`c:/Users/elec9/othello/othello/ui/sound.py` 생성:
```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"

try:
    from playsound import playsound  # type: ignore[import-not-found]
    _PLAYSOUND_OK = True
except ImportError:
    _PLAYSOUND_OK = False
    logger.info("playsound not installed; sound disabled")


def _play(name: str) -> None:
    if not _PLAYSOUND_OK:
        return
    path = ASSETS / name
    if not path.exists():
        logger.debug("sound file missing: %s", path)
        return
    try:
        playsound(str(path), block=False)
    except Exception as exc:  # noqa: BLE001 — 스펙대로 무시
        logger.debug("sound playback failed: %s", exc)


def play_place() -> None:
    _play("place.wav")


def play_flip() -> None:
    _play("flip.wav")


def play_win() -> None:
    _play("win.wav")
```

- [ ] **Step 2: GameScreen 에 사운드 연결**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 상단에 추가:
```python
from othello.ui import sound
```

`_play` 메서드에서 `self.state.play(move)` 가 성공한 직후에 `sound.play_place()` 호출:
```python
    def _play(self, move: Move) -> None:
        from othello.core.rules import flips_for
        flips = flips_for(self.state.board, move, self.state.current)
        try:
            self.state.play(move)
        except ValueError:
            return
        sound.play_place()
        self._hint_move = None
        # ... (이하 동일)
```

`_announce_winner` 의 다이얼로그 직전에 `sound.play_win()` 호출:
```python
    def _announce_winner(self) -> None:
        sound.play_win()
        # ... (이하 동일)
```

- [ ] **Step 3: 수동 스모크 테스트**

`python main.py` 실행. `assets/sounds/` 디렉터리는 아직 없어도 됩니다 — 게임이 크래시 없이 동작해야 합니다.

기대 동작:
- 터미널에 에러 없음 (playsound 미설치 시 info 로그 한 줄 정도).
- 모든 게임플레이가 정상 동작.
- 선택사항: `c:/Users/elec9/othello/assets/sounds/` 를 만들고 `place.wav`, `flip.wav`, `win.wav` 를 넣으면 실제 소리가 재생되는지 확인 가능.

- [ ] **Step 4: 커밋**

```bash
git add othello/ui/sound.py othello/ui/game_screen.py
git commit -m "feat(ui): add sound effects with graceful fallback"
```

---

## Task 21: UI — AI 턴 처리

**파일:**
- 수정: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: AI 팩토리 함수 + AI 턴 스케줄링 추가**

`c:/Users/elec9/othello/othello/ui/game_screen.py` 의 import 영역 근처에 모듈 함수 추가:
```python
def _build_strategy(name: str):
    if name == "random":
        from othello.ai.random_ai import RandomAI
        return RandomAI()
    if name == "greedy":
        from othello.ai.greedy import GreedyAI
        return GreedyAI()
    if name == "minimax":
        from othello.ai.minimax import MinimaxAI
        return MinimaxAI(depth=3)
    if name == "alphabeta":
        from othello.ai.alphabeta import AlphaBetaAI
        return AlphaBetaAI(depth=5)
    raise ValueError(f"Unknown AI: {name}")
```

`GameScreen.__init__` 에서 `self.state` 를 설정한 직후에 추가:
```python
        self.ai = None
        self.ai_color: Color | None = None
        if self.config_data.get("mode") == "vs_ai":
            self.ai = _build_strategy(self.config_data["ai_difficulty"])
            human = Color[self.config_data.get("human_color", "BLACK")]
            self.ai_color = human.opponent()
```

`__init__` 의 마지막 `self._refresh()` 다음에 추가:
```python
        self._maybe_schedule_ai()
```

`_play` 의 `after_anim` 콜백에 AI 턴 트리거 추가:
```python
        def after_anim() -> None:
            self._refresh()
            if self.state.is_over():
                self._announce_winner()
                return
            self._maybe_schedule_ai()
```

클래스에 AI 스케줄러 추가:
```python
    def _maybe_schedule_ai(self) -> None:
        if self.ai is None or self.ai_color is None:
            return
        if self.state.current is not self.ai_color:
            return
        if self.state.is_over():
            return
        # 애니메이션 끝나기를 기다린 뒤 잠시 후 실행
        self.after(300, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        if self.board_view.is_animating:
            self.after(100, self._run_ai_turn)
            return
        if self.ai is None or self.state.current is not self.ai_color:
            return
        try:
            move = self.ai.select_move(self.state)
        except ValueError:
            return
        self._play(move)
```

`from othello.core.board import Color` 가 이미 import 되어 있는지 확인 (Task 18 에서 추가됨).

- [ ] **Step 2: 수동 스모크 테스트**

`python main.py` 실행.

테스트 시나리오:
1. **vs Random, BLACK, 8×8:** 사용자가 먼저 두면 AI 가 빠르게 응수. 게임이 에러 없이 완료.
2. **vs Alpha-Beta, WHITE, 8×8:** AI 가 화면이 뜬 후 약 300ms 만에 첫 수를 두고 사용자 차례로 넘어옴.
3. **Hint 버튼:** vs AI 게임 중 사용자 차례에서 누르면 AlphaBeta 추천 수가 표시됨.
4. **AI 게임 중 Undo:** AI 가 둔 후 Undo 클릭 시 한 항목만 되돌아가므로 사용자 의사 결정 시점까지 가려면 두 번 누를 필요 있음. 이번 버전 한정으로 허용.
5. **중간 저장 → 메뉴 → 로드:** 저장한 게임이 AI 모드 포함 정상 복원.

확인 후 종료.

- [ ] **Step 3: 커밋**

```bash
git add othello/ui/game_screen.py
git commit -m "feat(ui): add AI opponent turn scheduling"
```

---

## Task 22: README 와 최종 스모크 테스트

**파일:**
- 수정: `othello/README.md`

- [ ] **Step 1: 전체 테스트 실행**

실행: `pytest -v`

기대 결과: 모든 테스트 통과 (~45개).

- [ ] **Step 2: core/ai 가 Tkinter 를 import 하지 않음을 확인**

실행:
```bash
python -c "import othello.core.game, othello.ai.alphabeta, othello.ai.minimax, othello.ai.greedy, othello.ai.random_ai, othello.ai.evaluation; import sys; assert 'tkinter' not in sys.modules, 'tkinter leaked into core/ai'; print('clean')"
```

기대 결과: `clean`. 실패 시 `core/` 또는 `ai/` 안의 잘못된 import 를 찾아 제거.

- [ ] **Step 3: 종합 수동 스모크 테스트**

`python main.py` 실행 후 다음을 순서대로 확인:

1. 메뉴 → 2P 6×6 시작 → 끝까지 진행 → 게임 종료 다이얼로그에 정확한 승자 표시.
2. 메뉴 → vs Greedy, BLACK, 8×8 → 몇 수 진행 → Undo 동작 → Hint 동작 → Save.
3. 메뉴 → Load Saved Game → 상태 복원 확인 → 계속 플레이.
4. 메뉴 → vs Alpha-Beta, 10×10 → AI 가 매 턴 약 2초 내 응수, UI 가 그 이상 멈추지 않음.
5. 메뉴 → 잘못된 로드 (취소 또는 비-JSON 파일) → 에러 다이얼로그 또는 무동작.

이상이 발견되면 커밋 전에 수정.

- [ ] **Step 4: README 갱신**

`c:/Users/elec9/othello/README.md` 를 다음으로 교체:
```markdown
# Othello

A desktop Othello (Reversi) game in Python with Tkinter, structured as a layered learning project: pure-functional `core/` engine, polymorphic `ai/` strategies, Tkinter `ui/`.

## Features

- 2-player local play and vs four AI strategies (Random, Greedy, Minimax, Alpha-Beta).
- Variable board size (6×6, 8×8, 10×10).
- Legal-move highlights, hint, undo, move history.
- Place and flip animations.
- JSON save/load via history replay.
- Optional sound effects (graceful fallback if missing).

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate    # Git-Bash on Windows; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

## Run

```
python main.py
```

## Test

```
pip install pytest
pytest
```

## Layout

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design.
```

- [ ] **Step 5: 커밋**

```bash
git add README.md
git commit -m "docs: flesh out README with features, setup, and run instructions"
```

---

## 자체 검토 메모

- **스펙 커버리지:**
  - §6 코어 엔진 → Task 2–8.
  - §7 AI 계층 → Task 9–13.
  - §8 UI 계층 → Task 15–21.
  - §9 영속화 → Task 14.
  - §10 테스트 → 각 TDD 단계에서 다루며 Task 22 에서 전체 검증.
  - §11 에러 처리 → 불법 클릭 무시(Task 18 `_on_click`), 저장 에러 다이얼로그(Task 18 `_save`, Task 16 `_load`), 사운드 실패 무시(Task 20).
  - §12 향후 작업 → 명시적으로 범위 외.

- **Task 8 보충 설명:** auto-pass 테스트는 보드 셀을 직접 조작해 인공 위치를 만듭니다. 검증 대상 규칙이 도달 경로와 무관하므로 허용됩니다. 자리표시자 `test_must_pass_detection` 은 의도적으로 남겨둔 문서용 마커입니다.

- **Task 18 vs Task 21 순서:** Task 18 에서 GameScreen 풀버전을 먼저 완성하고, Task 21 에서 메서드 몇 개만 추가해 AI 스케줄링을 붙입니다. 각 Task 가 독립적으로 검증 가능합니다.

- **애니메이션 단순화:** 뒤집기 애니메이션은 가로 폭을 줄였다가 늘리는 방식으로 회전을 모방합니다. 스펙 §8.5 의 "color crossfade or width-shrink-then-grow" 중 후자에 해당합니다.

- **vs AI 모드의 Undo:** Task 21 에 명시 — Undo 한 번이 history 한 항목을 되돌리므로, AI 게임에서 본인 의사결정 시점까지 가려면 두 번 눌러야 할 수 있습니다. 스펙 §6.3 정의(Undo는 한 항목 pop)와 일관되며 버그가 아닙니다.

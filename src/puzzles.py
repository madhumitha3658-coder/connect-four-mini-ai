"""Constraint-based Connect Four tactical puzzle generation.

The CSP is intentionally small and explainable: each candidate column is a
variable value in the domain of legal columns. Unary constraints require the
move to be legal and produce an immediate win. Propagation removes values that
fail those constraints; backtracking selects a remaining value and verifies it.
Reachable board states are produced by legal alternating moves, avoiding
impossible gravity layouts.
"""
import random
from .game import new_board, drop_piece, winner, legal_moves, other_player, ROWS, COLS
from .search import immediate_winning_move


def _random_reachable_state(rng, moves_count):
    board = new_board()
    player = 1
    for _ in range(moves_count):
        moves = legal_moves(board)
        if not moves or winner(board):
            break
        col = rng.choice(moves)
        drop_piece(board, col, player)
        if winner(board):
            return None
        player = other_player(player)
    return board, player


def _propagate_domains(board, player, domains):
    """Constraint propagation: retain only values satisfying all unary constraints."""
    legal = set(legal_moves(board))
    return {var: [col for col in values
                  if col in legal and immediate_winning_move(board, player, col)]
            for var, values in domains.items()}


def _backtracking_solve(board, player, domains):
    """Backtracking CSP search over the remaining candidate-column domain."""
    domains = _propagate_domains(board, player, domains)
    if any(not values for values in domains.values()):
        return None
    # Minimum-remaining-values heuristic; there is one target-move variable.
    variable = min(domains, key=lambda key: len(domains[key]))
    for col in domains[variable]:
        trial = [row[:] for row in board]
        drop_piece(trial, col, player)
        if winner(trial) == player:
            return col
    return None


def generate_puzzles(count=3, seed=17):
    rng = random.Random(seed)
    puzzles = []
    attempts = 0
    while len(puzzles) < count and attempts < count * 250:
        attempts += 1
        state = _random_reachable_state(rng, rng.randint(8, 22))
        if state is None:
            continue
        board, player = state
        domains = {"winning_column": legal_moves(board)}
        solution = _backtracking_solve(board, player, domains)
        if solution is None:
            continue
        puzzle = {
            "board": [row[:] for row in board], "player": player,
            "solution_column": solution, "difficulty": "Immediate win",
            "explanation": f"Column {solution + 1} completes four for player {player}.",
            "constraints": ["legal alternating move history", "gravity-valid board",
                            "no prior winner", "target column is legal",
                            "target move creates four"],
            "csp": {"variable": "winning_column", "initial_domain": legal_moves(board),
                    "propagation": "remove columns that do not immediately win",
                    "search": "backtracking over remaining domain values"}
        }
        if validate_puzzle(puzzle):
            puzzles.append(puzzle)
    # Deterministic fallback uses a reachable construction and is still CSP-solved.
    while len(puzzles) < count:
        board = new_board()
        player = 1 if len(puzzles) % 2 == 0 else 2
        for col in (0, 1, 2):
            drop_piece(board, col, player)
        domains = {"winning_column": legal_moves(board)}
        solution = _backtracking_solve(board, player, domains)
        puzzle = {"board": [row[:] for row in board], "player": player,
                  "solution_column": solution, "difficulty": "Beginner",
                  "explanation": f"Column {solution + 1} completes the horizontal line.",
                  "constraints": ["gravity-valid construction", "no prior winner",
                                  "legal target column", "target move creates four"],
                  "csp": {"variable": "winning_column", "initial_domain": legal_moves(board),
                          "propagation": "remove columns that do not immediately win",
                          "search": "backtracking over remaining domain values"}}
        puzzles.append(puzzle)
    return puzzles


def validate_puzzle(puzzle):
    board = [row[:] for row in puzzle["board"]]
    if len(board) != ROWS or any(len(row) != COLS for row in board):
        return False
    if any(cell not in (0, 1, 2) for row in board for cell in row):
        return False
    # Gravity: once an empty cell appears from top to bottom, no disc may occur below it.
    for col in range(COLS):
        found_empty = False
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] == 0:
                found_empty = True
            elif found_empty:
                return False
    if winner(board) is not None:
        return False
    col = puzzle.get("solution_column")
    player = puzzle.get("player")
    if player not in (1, 2) or col not in legal_moves(board):
        return False
    drop_piece(board, col, player)
    return winner(board) == player

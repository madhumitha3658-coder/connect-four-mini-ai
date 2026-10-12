import pytest
from src.game import new_board, drop_piece, winner, legal_moves
from src.search import choose_move, candidate_scores
from src.puzzles import generate_puzzles, validate_puzzle
from src.monte_carlo import evaluate_columns, simulate_match


def test_legal_moves_empty_board():
    assert len(legal_moves(new_board())) == 7


def test_horizontal_win():
    board = new_board()
    for col in range(4):
        drop_piece(board, col, 1)
    assert winner(board) == 1


def test_vertical_win():
    board = new_board()
    for _ in range(4):
        drop_piece(board, 2, 2)
    assert winner(board) == 2


def test_diagonal_win():
    board = new_board()
    board[2][0:4] = [1, 1, 1, 1]
    assert winner(board) == 1


def test_full_column_raises():
    board = new_board()
    for _ in range(6):
        drop_piece(board, 0, 1)
    assert 0 not in legal_moves(board)
    with pytest.raises(ValueError):
        drop_piece(board, 0, 2)


def test_search_takes_immediate_win():
    board = new_board()
    for col in (0, 1, 2):
        drop_piece(board, col, 1)
    move, _, _ = choose_move(board, 1, depth=3)
    assert move == 3


def test_search_restores_board():
    board = new_board()
    before = [row[:] for row in board]
    choose_move(board, 1, depth=2)
    assert board == before


def test_candidate_scores_include_all_legal_moves():
    board = new_board()
    assert {c for c, _, _ in candidate_scores(board, 1, depth=1)} == set(range(7))


def test_mc_has_each_legal_column():
    rows = evaluate_columns(new_board(), 1, rollouts=2, seed=3)
    assert {row["Column"] for row in rows} == set(range(1, 8))


def test_generated_puzzles_validate():
    puzzles = generate_puzzles(3, seed=17)
    assert len(puzzles) == 3
    assert all(validate_puzzle(puzzle) for puzzle in puzzles)
    assert all(puzzle["csp"]["search"].startswith("backtracking") for puzzle in puzzles)


def test_invalid_gravity_puzzle_rejected():
    board = new_board()
    board[0][0] = 1  # Floating disc
    puzzle = {"board": board, "player": 1, "solution_column": 1}
    assert not validate_puzzle(puzzle)


def test_simulation_runs():
    result = simulate_match(games=2, depth=1, rollouts_per_move=2, seed=4)
    assert result["games"] == 2
    assert result["minimax_wins"] + result["monte_carlo_wins"] + result["draws"] == 2

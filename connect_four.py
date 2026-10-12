
# Connect Four Mini AI using Minimax
# Search depth: 4 plies

ROWS = 6
COLS = 7
EMPTY = "."
HUMAN = "X"
AI = "O"
SEARCH_DEPTH = 4


# Create an empty game board
def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


# Display the board
def print_board(board):
    print("\n1 2 3 4 5 6 7")
    for row in board:
        print(" ".join(row))
    print()


# Get all valid columns
def valid_moves(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]


# Place a piece in the selected column
def drop_piece(board, col, piece):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = piece
            return row
    return -1


# Check whether a player has four pieces in a row
def has_won(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Diagonal: down-right
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Diagonal: up-right
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False


# Evaluate a group of four cells
def evaluate_window(window):
    score = 0
    ai_count = window.count(AI)
    human_count = window.count(HUMAN)
    empty_count = window.count(EMPTY)

    # Reward good AI opportunities
    if ai_count == 4:
        score += 100
    elif ai_count == 3 and empty_count == 1:
        score += 5
    elif ai_count == 2 and empty_count == 2:
        score += 2

    # Penalize human threats
    if human_count == 3 and empty_count == 1:
        score -= 6

    return score


# Static evaluation function for non-terminal boards
def evaluate_board(board):
    score = 0

    # Prefer the center column
    center = [board[r][COLS // 2] for r in range(ROWS)]
    score += center.count(AI) * 3

    # Evaluate horizontal groups
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c + i] for i in range(4)]
            score += evaluate_window(window)

    # Evaluate vertical groups
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = [board[r + i][c] for i in range(4)]
            score += evaluate_window(window)

    # Evaluate downward diagonal groups
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window)

    # Evaluate upward diagonal groups
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window)

    return score


# Minimax algorithm with depth-limited search
def minimax(board, depth, maximizing):
    if has_won(board, AI):
        return 100000 + depth, None

    if has_won(board, HUMAN):
        return -100000 - depth, None

    moves = valid_moves(board)

    if not moves:
        return 0, None

    # Stop searching at the selected depth
    if depth == 0:
        return evaluate_board(board), None

    if maximizing:
        best_score = float("-inf")
        best_col = moves[0]

        for col in moves:
            row = drop_piece(board, col, AI)

            score, _ = minimax(board, depth - 1, False)

            board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_col = col

        return best_score, best_col

    else:
        best_score = float("inf")
        best_col = moves[0]

        for col in moves:
            row = drop_piece(board, col, HUMAN)

            score, _ = minimax(board, depth - 1, True)

            board[row][col] = EMPTY

            if score < best_score:
                best_score = score
                best_col = col

        return best_score, best_col


# Main game loop
def play_game():
    board = create_board()

    print("CONNECT FOUR MINI AI - MINIMAX")
    print("You are X. The AI is O.")
    print("Search depth:", SEARCH_DEPTH)

    while True:
        print_board(board)

        # Human turn
        try:
            col = int(input("Choose a column (1-7): ")) - 1
        except ValueError:
            print("Please enter a valid number.")
            continue

        if col not in valid_moves(board):
            print("Invalid or full column. Try again.")
            continue

        drop_piece(board, col, HUMAN)

        if has_won(board, HUMAN):
            print_board(board)
            print("Congratulations! You win!")
            break

        if not valid_moves(board):
            print_board(board)
            print("The game is a draw!")
            break

        # AI turn
        print("AI is thinking...")
        score, ai_col = minimax(board, SEARCH_DEPTH, True)

        drop_piece(board, ai_col, AI)

        print("AI chooses column:", ai_col + 1)
        print("Evaluation score:", score)

        if has_won(board, AI):
            print_board(board)
            print("AI wins!")
            break

        if not valid_moves(board):
            print_board(board)
            print("The game is a draw!")
            break


if __name__ == "__main__":
    play_game()

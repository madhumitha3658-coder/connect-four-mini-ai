ROWS, COLS = 6, 7

def new_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def legal_moves(board):
    return [c for c in range(COLS) if 0 <= c < COLS and board[0][c] == 0]

def drop_piece(board, col, player):
    if not 0 <= col < COLS: raise ValueError("Column out of range")
    if player not in (1,2): raise ValueError("Player must be 1 or 2")
    for r in range(ROWS-1,-1,-1):
        if board[r][col] == 0:
            board[r][col]=player
            return r
    raise ValueError("Column is full")

def other_player(player): return 2 if player==1 else 1
def is_full(board): return not legal_moves(board)

def winner(board):
    for r in range(ROWS):
        for c in range(COLS):
            p=board[r][c]
            if not p: continue
            for dr,dc in ((0,1),(1,0),(1,1),(-1,1)):
                cells=[]
                for i in range(4):
                    rr,cc=r+dr*i,c+dc*i
                    if not (0<=rr<ROWS and 0<=cc<COLS): break
                    cells.append(board[rr][cc])
                if len(cells)==4 and all(v==p for v in cells): return p
    return None

def board_to_rows(board):
    return "\\n".join(" ".join({0:".",1:"R",2:"Y"}[v] for v in row) for row in board)

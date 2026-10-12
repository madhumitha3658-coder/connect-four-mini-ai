from .game import ROWS,COLS,legal_moves,drop_piece,winner,is_full,other_player

WIN=1_000_000

def evaluate(board,player):
    opp=other_player(player); score=0
    score += 7*sum(board[r][COLS//2]==player for r in range(ROWS))
    score -= 7*sum(board[r][COLS//2]==opp for r in range(ROWS))
    windows=[]
    for r in range(ROWS):
        for c in range(COLS-3): windows.append([board[r][c+i] for i in range(4)])
    for c in range(COLS):
        for r in range(ROWS-3): windows.append([board[r+i][c] for i in range(4)])
    for r in range(ROWS-3):
        for c in range(COLS-3): windows.append([board[r+i][c+i] for i in range(4)])
    for r in range(3,ROWS):
        for c in range(COLS-3): windows.append([board[r-i][c+i] for i in range(4)])
    for w in windows:
        own,enemy,empty=w.count(player),w.count(opp),w.count(0)
        if own==4: score+=100_000
        elif own==3 and empty==1: score+=80
        elif own==2 and empty==2: score+=10
        if enemy==3 and empty==1: score-=95
        elif enemy==2 and empty==2: score-=8
    return score

def immediate_winning_move(board,player,col):
    r=drop_piece(board,col,player); won=winner(board)==player; board[r][col]=0
    return won

def order_moves(board,player,moves,rule_based=True):
    if not rule_based: return list(moves)
    def rank(c):
        if immediate_winning_move(board,player,c): return (0,abs(c-COLS//2))
        if immediate_winning_move(board,other_player(player),c): return (1,abs(c-COLS//2))
        # Prefer central columns after urgent win/block checks.
        return (2,abs(c-COLS//2))
    return sorted(moves,key=rank)

def _search(board,depth,alpha,beta,maximizing,ai,pruning,rule_based,nodes):
    nodes[0]+=1
    res=winner(board)
    if res==ai: return WIN+depth
    if res==other_player(ai): return -WIN-depth
    moves=legal_moves(board)
    if depth<=0 or not moves: return evaluate(board,ai)
    current=ai if maximizing else other_player(ai)
    moves=order_moves(board,current,moves,rule_based)
    if maximizing:
        value=-float("inf")
        for c in moves:
            r=drop_piece(board,c,current)
            value=max(value,_search(board,depth-1,alpha,beta,False,ai,pruning,rule_based,nodes))
            board[r][c]=0
            if pruning:
                alpha=max(alpha,value)
                if alpha>=beta: break
        return value
    value=float("inf")
    for c in moves:
        r=drop_piece(board,c,current)
        value=min(value,_search(board,depth-1,alpha,beta,True,ai,pruning,rule_based,nodes))
        board[r][c]=0
        if pruning:
            beta=min(beta,value)
            if alpha>=beta: break
    return value

def choose_move(board,player,depth=4,pruning=True,rule_based=True):
    moves=legal_moves(board)
    if not moves: return None,0,0
    best_col,best_score=moves[0],-float("inf"); nodes=[0]
    for c in order_moves(board,player,moves,rule_based):
        r=drop_piece(board,c,player)
        score=_search(board,max(0,depth-1),-float("inf"),float("inf"),False,player,pruning,rule_based,nodes)
        board[r][c]=0
        if score>best_score: best_col,best_score=c,score
    return best_col,best_score,nodes[0]

def candidate_scores(board,player,depth=3,pruning=True,rule_based=True):
    out=[]
    for c in legal_moves(board):
        r=drop_piece(board,c,player); nodes=[0]
        score=_search(board,max(0,depth-1),-float("inf"),float("inf"),False,player,pruning,rule_based,nodes)
        board[r][c]=0; out.append((c,score,nodes[0]))
    return sorted(out,key=lambda x:x[1],reverse=True)

def explain_move(board,player,col):
    if col is None: return "No legal move is available."
    if immediate_winning_move(board,player,col): return f"Column {col+1} creates an immediate four-in-a-row win."
    if immediate_winning_move(board,other_player(player),col): return f"Column {col+1} blocks an immediate opponent win."
    if col==COLS//2: return f"Column {col+1} controls the centre, which participates in many possible winning lines."
    return f"Column {col+1} has the best estimated search score at the selected depth; the heuristic balances centre control and open four-cell patterns."

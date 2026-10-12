import random
from .game import new_board,legal_moves,drop_piece,winner,is_full,other_player
from .search import choose_move

def random_rollout(board,to_move,root_player,rng):
    b=[row[:] for row in board]; player=to_move
    while True:
        res=winner(b)
        if res: return 1 if res==root_player else 0
        moves=legal_moves(b)
        if not moves: return 0.5
        # Lightweight rollout policy: take a direct win, otherwise block a direct threat, else random.
        chosen=None
        for p in (player,other_player(player)):
            for c in moves:
                r=drop_piece(b,c,p); win=winner(b)==p; b[r][c]=0
                if win: chosen=c; break
            if chosen is not None: break
        if chosen is None: chosen=rng.choice(moves)
        drop_piece(b,chosen,player)
        res=winner(b)
        if res: return 1 if res==root_player else 0
        if is_full(b): return 0.5
        player=other_player(player)

def evaluate_columns(board,player,rollouts=40,seed=17):
    rng=random.Random(seed); rows=[]
    for col in legal_moves(board):
        wins=losses=draws=0
        r=drop_piece(board,col,player)
        res=winner(board)
        if res==player:
            wins=rollouts
        else:
            next_player=other_player(player)
            for _ in range(rollouts):
                outcome=random_rollout(board,next_player,player,rng)
                if outcome==1: wins+=1
                elif outcome==0: losses+=1
                else: draws+=1
        board[r][col]=0
        total=wins+losses+draws
        rows.append({"Column":col+1,"Wins":wins,"Losses":losses,"Draws":draws,"Win rate":round((wins+0.5*draws)/max(1,total),3),"Rollouts":rollouts})
    return rows

def simulate_match(games=6,depth=3,rollouts_per_move=12,seed=17):
    rng=random.Random(seed); results={"games":games,"minimax_wins":0,"monte_carlo_wins":0,"draws":0,"seed":seed,"depth":depth,"rollouts_per_move":rollouts_per_move}
    for game_idx in range(games):
        board=new_board(); turn=1
        # Alternate which agent starts to reduce first-player bias.
        mc_player=1 if game_idx%2==0 else 2
        while True:
            moves=legal_moves(board)
            if not moves: results["draws"]+=1; break
            if turn==mc_player:
                scores=evaluate_columns(board,turn,rollouts_per_move,rng.randrange(10**9))
                col=max(scores,key=lambda x:x["Win rate"])["Column"]-1
            else:
                col,_,_=choose_move(board,turn,depth,True,True)
            drop_piece(board,col,turn)
            res=winner(board)
            if res:
                if res==mc_player: results["monte_carlo_wins"]+=1
                else: results["minimax_wins"]+=1
                break
            turn=other_player(turn)
    return results

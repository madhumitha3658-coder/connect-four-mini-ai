from .game import COLS,drop_piece,winner,other_player
from .search import immediate_winning_move

def infer_move_reason(board,player,col):
    rules=[]
    if immediate_winning_move(board,player,col):
        rules.append("R1: If a legal move immediately completes four, choose that move.")
    elif immediate_winning_move(board,other_player(player),col):
        rules.append("R2: If the opponent has an immediate winning move, block that column.")
    elif col==COLS//2:
        rules.append("R3: If no immediate win/block dominates, prefer central control.")
    else:
        rules.append("R4: Otherwise compare heuristic scores for open lines and future threats.")
    rules.append(f"Inference trace: candidate column {col+1} evaluated; selected rule priority {rules[0][:2]}.")
    return "\n".join(rules)

def responsible_ai_notes():
    return [
      ("Transparency","The app exposes search depth, candidate scores, node counts and a short rule trace. Heuristic scores are approximations, not human-like reasoning."),
      ("Uncertainty","Monte Carlo results estimate outcomes from sampled rollouts. Small sample counts can vary; use a fixed seed for reproducibility and report the sample count."),
      ("Limitations","Depth-limited search can miss threats beyond the horizon. The rollout policy is simple and results depend on the current board and random seed."),
      ("Fairness and accountability","This is a deterministic board-game demonstration with no personal data. Users should not interpret game estimates as guarantees; maintainers should test edge cases and disclose limitations.")
    ]

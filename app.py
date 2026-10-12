import time
import pandas as pd
import streamlit as st
import plotly.express as px

from src.game import new_board, legal_moves, drop_piece, winner, is_full, other_player, board_to_rows
from src.search import choose_move, candidate_scores, explain_move, order_moves
from src.monte_carlo import evaluate_columns, simulate_match
from src.puzzles import generate_puzzles, validate_puzzle
from src.knowledge import infer_move_reason, responsible_ai_notes

st.set_page_config(page_title="Connect Four AI Lab", page_icon="🧠", layout="wide")
st.markdown("""
<style>
.stApp{background:radial-gradient(ellipse at 10% 0%,#1b2b4a 0%,#0b1120 52%,#070b14 100%);color:#eef3ff}
.block-container{max-width:1500px;padding-top:1.3rem}
h1,h2,h3{color:#f4f7ff}
div[data-testid="stMetric"]{background:#121e33;border:1px solid #2b3c5b;padding:12px;border-radius:14px}
div.stButton>button{border-radius:10px;border:1px solid #344b70;background:#182844;color:#f5f7ff;font-weight:700;min-height:40px}
div.stButton>button:hover{border-color:#67e8f9;color:#67e8f9}
.panel{background:linear-gradient(140deg,#152440,#101a2e);border:1px solid #2b3d5d;border-radius:16px;padding:16px;margin-bottom:12px}
.eyebrow{color:#67e8f9;font-size:.75rem;font-weight:800;letter-spacing:.16em}
</style>
""", unsafe_allow_html=True)

def init_state():
    defaults = {"board":new_board(),"history":[],"finished":False,"message":"Choose a column to begin.",
                "last_ai":None,"match_log":[],"puzzles":None,"puzzle_index":0,"puzzle_message":"",
                "puzzle_board":None,"puzzle_solution":None,"puzzle_moves":0}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init_state()

st.markdown('<div class="eyebrow">FOUNDATIONS OF AI · INTERACTIVE LAB</div>', unsafe_allow_html=True)
st.title("🧠 Connect Four AI Lab")
st.caption("Adversarial search · rule-based reasoning · Monte Carlo experiments · CSP puzzle generation")

with st.sidebar:
    st.header("Match settings")
    mode=st.selectbox("Mode",["Human vs AI","Human vs Human"])
    human_label=st.selectbox("Your disc",["Red","Yellow"],disabled=mode=="Human vs Human")
    human=1 if human_label=="Red" else 2
    depth=st.slider("Search depth",1,6,4)
    algorithm=st.radio("AI algorithm",["Alpha-Beta","Minimax"])
    use_ordering=st.checkbox("Use rule-based move ordering",value=True)
    if st.button("↻ Restart match",use_container_width=True):
        st.session_state.board=new_board(); st.session_state.history=[]; st.session_state.finished=False
        st.session_state.message="New match ready."; st.session_state.last_ai=None; st.rerun()
    if st.button("↶ Undo last turn",use_container_width=True,disabled=not st.session_state.history):
        count=2 if mode=="Human vs AI" and len(st.session_state.history)>=2 else 1
        for _ in range(count):
            if st.session_state.history: st.session_state.history.pop()
        b=new_board()
        for m in st.session_state.history: drop_piece(b,m["column"]-1,m["player_id"])
        st.session_state.board=b; st.session_state.finished=False; st.session_state.message="Last turn undone."
        st.session_state.last_ai=None; st.rerun()

tabs=st.tabs(["🎮 Play","🔎 Explainable AI","📊 Experiments","🧩 CSP Puzzle Lab","🛡️ Responsible AI"])

def record_move(col,player,label):
    drop_piece(st.session_state.board,col,player)
    st.session_state.history.append({"turn":len(st.session_state.history)+1,"player":label,"player_id":player,"column":col+1})
    result=winner(st.session_state.board)
    if result:
        st.session_state.finished=True
        st.session_state.message=("🏆 You win!" if result==human else "🤖 AI wins!") if mode=="Human vs AI" else f"🏆 {'Red' if result==1 else 'Yellow'} wins!"
        return True
    if is_full(st.session_state.board):
        st.session_state.finished=True; st.session_state.message="🤝 Draw — board is full."; return True
    return False

def do_move(col):
    if st.session_state.finished or col not in legal_moves(st.session_state.board): return
    if mode=="Human vs AI":
        human_moves=sum(m["player_id"]==human for m in st.session_state.history)
        ai_moves=sum(m["player_id"]!=human for m in st.session_state.history)
        if human_moves!=ai_moves: return
        if record_move(col,human,"You"): return
        ai=other_player(human)
        started=time.perf_counter()
        ai_col,score,nodes=choose_move(st.session_state.board,ai,depth,algorithm=="Alpha-Beta",use_ordering)
        elapsed=time.perf_counter()-started
        st.session_state.last_ai={"column":ai_col+1,"score":score,"nodes":nodes,"seconds":elapsed,"depth":depth,"algorithm":algorithm,"ordering":use_ordering}
        if ai_col is not None: record_move(ai_col,ai,"AI")
    else:
        p=1 if len(st.session_state.history)%2==0 else 2
        record_move(col,p,"Red" if p==1 else "Yellow")
    if not st.session_state.finished: st.session_state.message="Choose the next column."

with tabs[0]:
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.markdown('<div class="panel"><div class="eyebrow">LIVE MATCH</div><h3>Choose a lane</h3>Discs fall to the lowest empty cell in each column.</div>',unsafe_allow_html=True)
        st.info(st.session_state.message)
        cols=st.columns(7)
        for c in range(7):
            with cols[c]:
                if st.button(f"▼ {c+1}",key=f"play_{c}",disabled=st.session_state.finished or c not in legal_moves(st.session_state.board),use_container_width=True):
                    do_move(c); st.rerun()
        symbols={0:"⚫",1:"🔴",2:"🟡"}
        board_html='<div style="background:linear-gradient(140deg,#2459a5,#153a78);padding:12px;border-radius:18px;border:2px solid #5387d5">'
        for row in st.session_state.board:
            board_html+='<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:7px;margin-bottom:7px">'
            for v in row:
                bg="#091329" if v==0 else "#ff4f70" if v==1 else "#ffd166"
                board_html+=f'<div style="aspect-ratio:1;border-radius:50%;background:{bg};border:2px solid #ffffff25;box-shadow:inset 0 4px 8px #0008"></div>'
            board_html+='</div>'
        board_html+='</div>'
        st.markdown(board_html,unsafe_allow_html=True)
        st.caption("🔴 Red · 🟡 Yellow · ⚫ Empty")
    with right:
        st.markdown('<div class="panel"><div class="eyebrow">AI TELEMETRY</div><h3>Last decision</h3></div>',unsafe_allow_html=True)
        last=st.session_state.last_ai
        if last:
            a,b=st.columns(2); a.metric("Chosen column",last["column"]); b.metric("Nodes searched",f'{last["nodes"]:,}')
            a.metric("Depth",last["depth"]); b.metric("Search time",f'{last["seconds"]:.5f}s')
            st.caption(f'{last["algorithm"]} · rule ordering: {last["ordering"]} · score: {last["score"]}')
        else: st.write("AI statistics appear after the first AI move.")
        st.markdown("#### Move history")
        if st.session_state.history:
            st.dataframe(pd.DataFrame([{k:v for k,v in m.items() if k not in ("player_id",)} for m in st.session_state.history]),hide_index=True,use_container_width=True)
        else: st.caption("No moves yet.")

with tabs[1]:
    st.subheader("Explain a position")
    expl_player=st.selectbox("Analyse for",["Red","Yellow"],key="expl_player")
    expl_id=1 if expl_player=="Red" else 2
    if st.button("Analyse current board",key="analyse"):
        scores=candidate_scores(st.session_state.board,expl_id,depth,True,True)
        if scores:
            best=scores[0][0]
            st.success(explain_move(st.session_state.board,expl_id,best))
            st.write(infer_move_reason(st.session_state.board,expl_id,best))
            st.dataframe(pd.DataFrame([{"Column":c+1,"Search score":s,"Nodes":n} for c,s,n in scores]),hide_index=True,use_container_width=True)
        else: st.warning("No legal moves remain.")

with tabs[2]:
    st.subheader("Experiment 1 · Move ordering and node counts")
    st.write("Uses the current board and selected player. Both runs use the same depth and position.")
    exp_player=st.selectbox("Experiment player",["Red","Yellow"],key="exp_player")
    exp_id=1 if exp_player=="Red" else 2
    if st.button("Run node-count comparison"):
        a=choose_move(st.session_state.board,exp_id,depth,True,False)
        b=choose_move(st.session_state.board,exp_id,depth,True,True)
        st.session_state.order_result={"Without ordering":{"column":a[0]+1 if a[0] is not None else None,"nodes":a[2]},
                                       "With rule ordering":{"column":b[0]+1 if b[0] is not None else None,"nodes":b[2]}}
    if "order_result" in st.session_state:
        st.dataframe(pd.DataFrame([{"Method":k,**v} for k,v in st.session_state.order_result.items()]),hide_index=True,use_container_width=True)
        x=st.session_state.order_result
        if x["Without ordering"]["nodes"]:
            reduction=(1-x["With rule ordering"]["nodes"]/x["Without ordering"]["nodes"])*100
            st.metric("Node-count change",f"{reduction:.1f}%",help="Positive means fewer nodes with ordering; negative means more nodes.")
    st.divider()
    st.subheader("Experiment 2 · Monte Carlo rollouts by column")
    st.caption("Each legal first move is evaluated using random rollouts. Results vary with the random seed.")
    sims=st.slider("Rollouts per column",10,200,40,10)
    seed=st.number_input("Random seed",min_value=0,max_value=999999,value=17)
    mc_player=st.selectbox("Rollout player",["Red","Yellow"],key="mc_player")
    mc_id=1 if mc_player=="Red" else 2
    if st.button("Run Monte Carlo column analysis"):
        rows=evaluate_columns(st.session_state.board,mc_id,sims,int(seed))
        st.session_state.mc_rows=rows
    if "mc_rows" in st.session_state and st.session_state.mc_rows:
        df=pd.DataFrame(st.session_state.mc_rows)
        st.dataframe(df,use_container_width=True,hide_index=True)
        fig=px.bar(df,x="Column",y="Win rate",color="Win rate",range_y=[0,1],title="Monte Carlo estimated win rate by first column")
        st.plotly_chart(fig,use_container_width=True)
    st.divider()
    st.subheader("Experiment 3 · AI match simulation")
    games=st.slider("Games in batch",2,30,6,2)
    if st.button("Simulate Minimax vs Monte Carlo"):
        with st.spinner("Simulating games..."):
            result=simulate_match(games,depth,rollouts_per_move=max(8,sims//2),seed=int(seed))
        st.session_state.match_result=result
    if "match_result" in st.session_state:
        st.json(st.session_state.match_result)

with tabs[3]:
    st.subheader("CSP-based puzzle generator")
    st.write("The generator treats the winning column as a CSP variable. Its domain begins with legal columns; constraint propagation removes columns that do not win immediately, and backtracking verifies a remaining value.")
    count=st.slider("Puzzles to generate",3,5,3)
    if st.button("Generate and validate puzzles"):
        st.session_state.puzzles=generate_puzzles(count,seed=17)
    if st.session_state.puzzles:
        for i,p in enumerate(st.session_state.puzzles,1):
            with st.expander(f"Puzzle {i} · {p['difficulty']} · target column {p['solution_column']+1}",expanded=i==1):
                st.code(board_to_rows(p["board"]),language=None)
                st.write(f"Player to move: {'Red' if p['player']==1 else 'Yellow'}")
                st.write(f"Validation: {'PASS' if validate_puzzle(p) else 'FAIL'}")
                st.write(f"Reason: {p['explanation']}")
                st.write(f"Constraint checks: {', '.join(p['constraints'])}")
                if p.get("csp"):
                    st.write("**CSP formulation**")
                    st.json(p["csp"])

with tabs[4]:
    st.subheader("Responsible AI and limitations")
    for heading,body in responsible_ai_notes():
        with st.expander(heading): st.write(body)
    st.info("Search scores and Monte Carlo estimates are decision aids, not guarantees. Report measured results from your own runs.")

st.markdown("---")
st.caption("Connect Four AI Lab · Minimax · Alpha-Beta · Monte Carlo · CSP · Explainable AI")

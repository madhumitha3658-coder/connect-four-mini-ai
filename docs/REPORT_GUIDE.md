# Final report guide — Connect Four AI Lab

Use this guide to write the final 4–6 page report for the Explainable Connect Four with Puzzle Generator extension. Replace every bracketed item with results and screenshots from your own run; do not invent experiment results.

## 1. Problem statement and objectives
Describe Connect Four as a two-player, deterministic, turn-taking game. State the objective: build an AI that selects legal moves and explain its choices, compare search and rollout behaviour, and generate tactical puzzles.

## 2. AI formulation and methods
- **State:** 6 × 7 board with values 0 (empty), 1 (Red), and 2 (Yellow).
- **Actions:** choose a non-full column.
- **Transition:** a disc falls to the lowest empty cell.
- **Terminal test:** four matching discs in a row, column, or diagonal, or a full board.
- **Minimax:** explores alternating maximizing/minimizing decisions to a selected depth; the static heuristic rewards centre control and open four-cell windows and penalizes opponent threats.
- **Alpha–Beta:** prunes branches that cannot change the current decision.
- **Move ordering / rule base:** immediate win → block opponent immediate win → prefer centre → compare heuristic scores.
- **Monte Carlo:** samples completions from each legal first move. Estimates depend on rollout count, rollout policy, position, and seed.

## 3. Explainability and CSP puzzle generation
Describe the chosen column, score, explored-node count, and rule trace shown by the interface. For the CSP, define `winning_column` as the variable and legal columns as its initial domain. Constraints require a legal move, a gravity-valid reachable board, no pre-existing winner, and an immediate win after the target move. Propagation filters columns that do not satisfy the immediate-win constraint; backtracking verifies candidate values. Explain that this is a deliberately small single-variable CSP, not a general-purpose solver.

## 4. Experiments and results
Record the configuration and actual measurements from your own run:

| Experiment | Configuration to record | Your measured result |
|---|---|---|
| Move ordering | board/position, depth, node count with and without ordering | [insert actual values] |
| Monte Carlo per-column analysis | player, rollouts per column, seed, win-rate chart | [insert observations] |
| Minimax vs Monte Carlo | games, search depth, rollouts per move, seed, wins/losses/draws | [insert actual values] |
| Puzzle generation | puzzle count, validation pass count, example solution | [insert actual values] |

Do not assume move ordering always reduces node count; report the measured outcome and explain that results depend on the position and search depth.

## 5. Testing and screenshots
Run `python -m pytest -q` and report the result shown in your terminal. Include screenshots of the live board, explainability tab, node-count comparison, Monte Carlo chart, CSP puzzle lab, and Responsible AI tab. Screenshots must come from your own running application.

## 6. Responsible AI, limitations, and conclusion
Mention that the app uses no personal data; heuristic scores and rollout outcomes are estimates, not guarantees; depth-limited search may miss threats beyond its horizon; and results can vary with Monte Carlo sampling. Summarize what the experiments demonstrate and identify one improvement.

## Run and test
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

# Connect Four AI Lab

A Streamlit application demonstrating adversarial search, explainable move selection, Monte Carlo rollouts, CSP-style puzzle validation, and Responsible AI notes.

## Features
- Human vs AI and local Human vs Human gameplay
- Depth-limited Minimax and Alpha-Beta pruning
- Rule-based move ordering: immediate win, block, then centre preference
- Node-count comparison with and without move ordering
- Monte Carlo per-column win/loss/draw estimates and chart
- Minimax vs Monte Carlo batch simulation
- CSP puzzle generation using a winning-column variable, legal-column domain, constraint propagation, and backtracking verification
- Move explanation, rule trace, and Responsible AI notes
- Automated tests

## Run on Windows PowerShell
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

## AI formulation
State: a 6×7 board. Action: choose a legal column. Transition: the disc drops to the lowest empty row. Terminal states: four in a row or full board. The heuristic values centre control and four-cell windows. Minimax explores to a selected depth; Alpha-Beta prunes branches that cannot change the decision.

## Experiments
The app provides node counts for the same board/depth with and without rule-based move ordering, per-column Monte Carlo rollout estimates with a configurable seed, and a batch Minimax-versus-Monte-Carlo match simulation. Record the actual values from your own runs; results depend on position, depth, rollout count, and seed.

## CSP formulation
The puzzle generator builds reachable board states by alternating legal moves. It models `winning_column` as a CSP variable whose initial domain is the set of legal columns. Constraints require a legal target and an immediate four-in-a-row win, while the board must satisfy gravity and have no pre-existing winner. Constraint propagation removes columns that do not satisfy the immediate-win constraint; backtracking checks remaining values and verifies the resulting state. This is a small, single-variable CSP tailored to tactical puzzles, not a general-purpose CSP engine or a full arc-consistency implementation. State this scope honestly in the report.

## Limitations and Responsible AI
The heuristic is approximate and search can miss tactics beyond its depth horizon. Monte Carlo outcomes are estimates, not guarantees. A fixed seed improves reproducibility. No personal data is collected.

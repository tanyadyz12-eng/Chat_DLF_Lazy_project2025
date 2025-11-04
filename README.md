[README.md](https://github.com/user-attachments/files/23345531/README.md)

# Lazor Project — README (English Only)

A concise, TA-ready submission for the Lazor course project. This repository provides **single-board runs**, **batch evaluation**, and **artifact export** (TXT/JSON/PNG). It supports two collision models and two solver modes.

---

## 1) What’s Included

**Entrypoints**
- `lazor_solver/main_plus.py` — full-featured CLI with `--collision`, `--solver`, `--png`, etc.
- `lazor_solver/main_unified.py` — simplified entry for the default course configuration (fixed `v2`).

**Batch runners**
- `lazor_solver/run_all_wall.py` — batch run over a folder of `.bff` with **wall + v2**, writes `summary_wall.csv`.
- `lazor_solver/run_all_unified.py` — runs the four combos **(wall|center) × (v2|parallel)**, writes `summary_unified.csv`.

**Simulation backends**
- `lazor_solver/simulate_wall.py` — wall-collision tracer (default for submission).
- `lazor_solver/simulate.py` — center-collision tracer (for comparison/robustness).

**Solvers**
- `lazor_solver/solver_v2.py` — main backtracking + heuristics solver (supports time limits and seed).
- `lazor_solver/solver_parallel.py` — parallel wrapper (multi-process / multi-seed exploration).

**I/O & Rendering**
- `lazor_solver/render_plus.py` — unified writer for TXT/JSON/PNG artifacts.
- `lazor_solver/render.py` — enhanced PNG renderer; auto-infers hits when not explicitly provided.

**Core types & parsing**
- `lazor_solver/model.py` — data structures (Board, Block, BlockType, etc.).
- `lazor_solver/bff_parser.py` — parses `.bff` into a `Board` instance.

**Smoke tests**
- `lazor_solver/test_basic.py` — minimal tests for parser, block creation, and tracing.

> Coordinates: lattice intersections are integers; block centers live at odd coordinates (half‑step model) to match the class BFF spec.

---

## 2) Environment

- Python ≥ 3.8 (3.9+ recommended)
- No third-party dependencies are strictly required for solving. PNG export requires a working `matplotlib` installation available on the grader machine (already used in many course setups).

Suggested layout:

```
<repo_root>/
  boards/               # the instructor's .bff tests
  results/              # output dir (created automatically if missing)
  lazor_solver/
    main_plus.py
    main_unified.py
    run_all_wall.py
    run_all_unified.py
    bff_parser.py
    model.py
    simulate_wall.py
    simulate.py
    solver_v2.py
    solver_parallel.py
    render_plus.py
    render.py
```

---

## 3) Quick Start (single board)

Run **wall + v2** (recommended for course grading). Exports `.txt/.json` and optional `.png` to `results/`:

```bash
python3 lazor_solver/main_plus.py boards/dark_1.bff \
  --collision wall --solver v2 --time_limit 120 --png 1 \
  --seed 42 --out results --results_dir results
```

Common flags:
- `--collision {wall|center}` — collision model.
- `--solver {v2|parallel}` — single-threaded `v2` or parallel search.
- `--time_limit` — seconds per board.
- `--png {0|1}` — export PNG visualization.
- `--seed` — random seed for reproducibility.
- `--workers` — process count for `--solver parallel`.

**Simplified entry (fixed v2):**
```bash
python3 lazor_solver/main_unified.py boards/dark_1.bff \
  --collision wall --time_limit 120 --png 1 --seed 42 --out results
```

---

## 4) Batch Evaluation

**A. Default course setting (wall + v2):**
```bash
python3 lazor_solver/run_all_wall.py \
  --boards_dir boards --results_dir results --time_limit 120 --png 1 --seed 42
```
Artifacts: `results/summary_wall.csv` plus per-board TXT/JSON(/PNG).

**B. Full comparison (wall/center × v2/parallel):**
```bash
python3 lazor_solver/run_all_unified.py \
  --boards_dir boards --results_dir results --time_limit 120 --png 1 --seed 42 --workers 4
```
Artifacts: `results/summary_unified.csv` plus per-board outputs for each combo.

---

## 5) Output Artifacts

For each `NAME.bff` and each (collision, solver) pair, you will find:
- `NAME_{collision}_{solver}.txt` — human-readable summary (solved flag, elapsed, seed, etc.).
- `NAME_{collision}_{solver}.json` — machine-readable summary for autograding.
- `NAME_{collision}_{solver}.png` — optional visualization (targets, hits, blocks, path).

---

## 6) Reproducibility & Parallelism

- Set `--seed` for deterministic exploration within a given heuristic schedule.
- `solver_parallel.py` distributes multiple seeds across processes to broaden the search and reduce the chance of local optima.
- Respect `--time_limit` to stay within grading constraints.

---

## 7) Minimal Tests

Run basic smoke tests (requires `boards/dark_1.bff` present):

```bash
python3 lazor_solver/test_basic.py
```

This checks:
1) `.bff` parsing returns a valid board,  
2) Block construction,  
3) `simulate_wall.trace` returns `(hits, trajectory)` with correct types.

---

## 8) Troubleshooting

- **Only FAIL results**: confirm `boards/` path and file names; try a few different `--seed` values or use `--solver parallel --workers 4`.
- **No PNG created**: ensure `--png 1` and `matplotlib` is available; `render_plus.py` calls into `render.py` for visualization.
- **Different collision behavior**: use `--collision wall` for the default submission unless your instructor requests otherwise.
- **Timeouts**: lower PNG usage for speed, or use `parallel` mode; verify per-board elapsed time is ≤ 120 s.

---

## 9) Grading Checklist

- [ ] All required boards solved under `--time_limit 120` using **wall + v2**.  
- [ ] `results/` contains `.txt` + `.json` (PNG optional but recommended).  
- [ ] CLI works out-of-the-box from TA’s machine (paths resolvable; no hard-coded OS specifics).  
- [ ] Public, well-commented code and function docstrings where appropriate.  
- [ ] README includes exact commands to reproduce results.

---

## 10) Notes for Reviewers (Design Highlights)

- `render.py` enhances PNG clarity (legend, inferred hits, turn labels) and tolerates callers that omit `hits`.  
- `solver_v2.py` favors progress-aware heuristics and maintains the best partial solution within the time budget.  
- `test_basic.py` offers a quick sanity check to prevent trivial environment or import errors before batch runs.



---

## Submission Quick Start (for TAs)

```bash
# Single board (wall+v2)
python3 lazor_solver/main_plus.py boards/dark_1.bff \
  --collision wall --solver v2 --time_limit 120 --png 1 \
  --seed 42 --out results --results_dir results

# Batch (7 boards, wall+v2)
python3 lazor_solver/run_all_wall.py \
  --boards_dir boards --results_dir results --time_limit 120 --png 1 --seed 42
```

Artifacts expected: `results/*.txt`, `results/*.json`, and `results/summary_wall.csv` (PNG optional).  
Time budget: **≤120 seconds per board**.


## Authors
- Yizhe Ding
- Zhihan Liu
- Qian Fu

# Lazor Project — EN.540.635 (Fall 2025)

This repository implements a reproducible Lazor solver using only the Python standard library. It provides a CLI entry point, batch runners, and consistent outputs (JSON/TXT/PNG) for grading and verification.

## Repository layout

```
.
├── boards/                 # Test maps (.bff)
├── results/                # Outputs (auto-created)
├── README.md
├── bff_parser.py
├── main_plus.py            # Primary CLI entry
├── main_unified.py         # Alternate entry (legacy-compatible)
├── model.py
├── render.py
├── render_plus.py
├── run_all_unified.py      # Batch runner (recommended)
├── run_all_wall.py         # Batch runner for wall collision
├── simulate.py             # Center-collision model (not used for submission)
├── simulate_wall.py        # Wall-collision model (used)
├── solver_v2.py            # Heuristic backtracking solver (used)
├── solver_parallel.py      # Multi-process wrapper (optional)
└── test_basic.py           # Simple sanity checks
```

**Dependencies:** Python ≥ 3.10, no third-party packages required.

---

## Quick start (single map)

Example (wall collision, `v2` solver):

```bash
python3 main_plus.py boards/dark_1.bff --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results
```

Key arguments:
- `--collision {wall|center}`: collision model (submission uses `wall`)
- `--solver {v2|parallel}`: solver choice (`v2` recommended; `parallel` optional)
- `--time_limit <seconds>`: per-map time budget (default 120)
- `--png {0|1}`: save a PNG visualization
- `--seed <int>`: RNG seed for reproducibility
- `--out`, `--results_dir`: output folders (default `results`)

---

## Recommended demo maps (reproducible commands)

```bash
# 1) dark_1
python3 main_plus.py boards/dark_1.bff --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results

# 2) mad_1
python3 main_plus.py boards/mad_1.bff  --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results

# 3) mad_7
python3 main_plus.py boards/mad_7.bff  --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results

# 4) choose the one that exists in your boards/: showstopper_4 or tiny_5
python3 main_plus.py boards/showstopper_4.bff --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results
# or
python3 main_plus.py boards/tiny_5.bff       --collision wall --solver v2 --time_limit 120 --png 1 --seed 42 --out results --results_dir results
```

All outputs are written under `results/` within the time limit.

---

## Batch runs

Run all `.bff` files in `boards/`:

```bash
python3 run_all_unified.py --boards_dir boards --results_dir results --time_limit 120 --png 1 --workers 4
```

Wall-only batch (optional):

```bash
python3 run_all_wall.py --boards_dir boards --results_dir results --time_limit 120 --png 1
```

---

## Output format (results/)

For each map, three files are produced using the pattern `<board>_<collision>_<solver>.*`:
- `.json` — machine-readable summary
- `.txt`  — human-readable placement summary
- `.png`  — visualization (if `--png 1`)

Example JSON:
```json
{
  "board": "dark_1_wall_v2",
  "solved": true,
  "elapsed": 0.123,
  "seed": 42,
  "collision": "wall",
  "solver": "v2",
  "hits": 2,
  "targets": 2,
  "placements": { "(r,c)": "A" }
}
```

Quick pass/fail grep:
```bash
grep -H '"solved":' results/*_wall_v2.json
```

---

## Implementation notes

- **Parsing:** `bff_parser.py` converts `.bff` into `Board/Block` structures (coordinate system aligned with course spec).
- **Simulation:** `simulate_wall.py` traces rays on the grid with reflection/absorption/refraction rules.
- **Solvers:** `solver_v2.py` uses backtracking with slot/block ordering heuristics, time limit, and a reproducible seed.  
  `solver_parallel.py` offers a multi-process exploration wrapper.
- **Rendering:** `render_plus.py` writes JSON/TXT/PNG artifacts for grading and visualization.

---

## Environment

- Python ≥ 3.10  
- OS: Windows / macOS / Linux  
- No external libraries required

---

## FAQ

- **File not found:** `cd` to the repo root before running, or use absolute paths.  
- **No PNG generated:** pass `--png 1` and ensure `results/` exists (it is auto-created).  
- **Time budget:** adjust `--time_limit`; start with the recommended demo maps first.  
- **Reproducibility:** commands specify `--seed`; change it to explore alternative solutions if desired.

---

## License / Academic use

For EN.540.635 coursework use. Please acknowledge this repository if you reuse code or ideas.

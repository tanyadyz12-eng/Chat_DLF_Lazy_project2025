[README.md](https://github.com/user-attachments/files/23350703/README.md)
# Lazor Board Game Solver

A Python-based solver for the Lazor board game. It loads `.bff` boards, simulates laser–block interactions under the **wall** collision model, and searches for placements that hit all targets within a **120-second per-board** cap.

## Team
- **Yizhe Ding**
- **Zhihan Liu**
- **Qian Fu**

Repository: https://github.com/tanyadyz12-eng/Chat_DLF_Lazy_project2025

---

## 1) Overview
- Reads instructor `.bff` files from `bff_files/`
- Supports fixed blocks and all three movable block types
- Produces human-readable solutions (and optionally machine-readable JSON and annotated PNGs)
- Deterministic runs optional via a fixed `seed`
- Per-board **time limit = 120 s**

### Physics Rules (Collision = `wall`)
- **A (Reflect)**: mirror reflection about the surface normal  
- **B (Opaque)**: absorbs the ray (terminates)  
- **C (Refract-like)**: continue straight **and** spawn one mirror-reflected ray  
- **Targets**: considered hit **only** when a ray passes **exactly through a lattice intersection** (grid vertex)  
- **Fixed blocks**: pre-placed blocks in `.bff` must remain in place  
- **Walls**: outer borders reflect like A blocks

---

## 2) Quick Start

> Commands assume the current repository structure in your project.

### Solve a single board
```bash
cd bff_files
python lazor_solver.py mad_1.bff
```

### Solve all boards in the folder
```bash
cd bff_files
python lazor_solver.py
```

**Time cap**: each board is capped at **120 s**.

---

## 3) Files & Outputs

### Inputs
- `bff_files/*.bff` — instructor test boards

### Minimum outputs (current build)
- `bff_files/*_solution.txt` — human-readable placement and verification

### Recommended optional outputs (for grading clarity)
- `solutions/*.json` — structured results; suggested fields:
  ```json
  {
    "board": "mad_1",
    "solver": "default",
    "collision": "wall",
    "solved": true,
    "elapsed": 0.34,
    "seed": 42,
    "placements": [{"type": "A", "x": 2, "y": 1}],
    "targets": [{"x": 3, "y": 0, "hit": true}]
  }
  ```
- `solutions/*.png` — annotated ray traces (paths + hit markers, with `elapsed/seed` corner label)

**Naming convention**
```
<board>_wall_<solver>.(txt|json|png)
```

---

## 4) Environment
- **Python**: 3.10 or 3.11 recommended (single-file version runs on 3.6+)  
- **Dependencies**: standard library only for the single-file version  
  - If PNG/JSON exporters or batch tools are added, include `requirements.txt` and install via:
    ```bash
    python -m pip install -r requirements.txt
    ```

---

## 5) Results Summary (template)
Replace the times with your actual measurements if you include JSON or logs.

| Board | Time (s) | Solved |
|------|----------:|:------:|
| dark_1.bff | <0.01 | ✓ |
| tiny_5.bff | <0.01 | ✓ |
| showstopper_4.bff | 0.01 | ✓ |
| mad_1.bff  | 0.01  | ✓ |
| mad_4.bff  | 0.34  | ✓ |
| numbered_6.bff | 0.51 | ✓ |
| mad_7.bff  | 3.31  | ✓ |
| yarn_5.bff | 7.65  | ✓ |

> Tip: If you export `solutions/*.json`, you can aggregate to a CSV and paste a Markdown table here.

---

## 6) Testing
If tests are included:
```bash
python -m pytest -q
```
Suggested coverage: malformed `.bff` error messages; A/B/C physics behavior; fixed-seed repeatability on a tiny board.

---

## 7) Submission Checklist
- Quick-start commands (single + all) are documented and runnable  
- Physics rules match the assignment (A mirror, B absorb, C straight+reflect; targets = lattice intersections; walls reflect)  
- Per-board time cap = **120 s** stated  
- Outputs include `*_solution.txt`; optional JSON/PNG follow the naming and field suggestions  
- README and boards are present to reproduce results

---

## 8) Acknowledgments
Implemented according to the assignment handout. No third‑party solver libraries are used.

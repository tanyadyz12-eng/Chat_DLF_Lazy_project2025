
"""
run_all_unified.py
Batch runner that runs each .bff with both collision models (wall, center)
and both solvers (v2, parallel) and writes a comparison CSV.
"""
from __future__ import annotations
import argparse, os, subprocess, shlex, csv, itertools

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards_dir", default="boards")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--results_dir", default="results")
    args = ap.parse_args()

    os.makedirs(args.results_dir, exist_ok=True)
    boards = sorted([f for f in os.listdir(args.boards_dir) if f.endswith(".bff")])

    combos = list(itertools.product(["wall","center"], ["v2","parallel"]))
    rows = []
    for name in boards:
        bff_path = os.path.join(args.boards_dir, name)
        for collision, solver in combos:
            entry = f"{collision}/{solver}"
            exe = "main_plus.py" if solver == "parallel" else "main_plus.py"
            cmd = f"python {exe} {bff_path} --collision {collision} --solver {solver} --time_limit {args.time_limit} --png {args.png} --seed {args.seed} --workers {args.workers} --results_dir {args.results_dir}"
            print("[RUN]", cmd)
            try:
                out = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
                msg = out.decode("utf-8", errors="ignore").strip()
            except subprocess.CalledProcessError as e:
                msg = e.output.decode("utf-8", errors="ignore").strip()
            rows.append([name, collision, solver, args.time_limit, args.png, args.seed, args.workers, msg])

    csvp = os.path.join(args.results_dir, "summary_unified.csv")
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["board","collision","solver","time_limit","png","seed","workers","message"])
        for r in rows: w.writerow(r)
    print("[OK] Comparison written:", csvp)

if __name__ == "__main__":
    main()

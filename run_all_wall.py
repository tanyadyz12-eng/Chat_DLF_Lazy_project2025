
"""
run_all_wall.py
Batch runner for all .bff using wall-collision via main_unified.py
"""
from __future__ import annotations
import argparse, os, subprocess, shlex, csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards_dir", default="boards")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--results_dir", default="results")
    args = ap.parse_args()

    os.makedirs(args.results_dir, exist_ok=True)
    boards = sorted([f for f in os.listdir(args.boards_dir) if f.endswith(".bff")])

    rows = []
    for name in boards:
        bff_path = os.path.join(args.boards_dir, name)
        cmd = f"python main_unified.py {bff_path} --collision wall --time_limit {args.time_limit} --png {args.png} --seed {args.seed} --results_dir {args.results_dir}"
        print("[RUN]", cmd)
        try:
            out = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
            msg = out.decode("utf-8", errors="ignore").strip()
        except subprocess.CalledProcessError as e:
            msg = e.output.decode("utf-8", errors="ignore").strip()
        rows.append([name, args.time_limit, args.png, args.seed, msg])

    txt = os.path.join(args.results_dir, "summary_wall.txt")
    csvp = os.path.join(args.results_dir, "summary_wall.csv")
    with open(txt, "w", encoding="utf-8") as f:
        for r in rows: f.write("\t".join(map(str, r)) + "\n")
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["board","time_limit","png","seed","message"])
        for r in rows: w.writerow(r)

    print("[OK] Summary written:", txt, "and", csvp)

if __name__ == "__main__":
    main()

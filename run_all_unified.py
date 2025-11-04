#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, subprocess, shlex, csv, itertools, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--boards_dir", default="boards")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--png", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--results_dir", default="results")
    args=ap.parse_args()

    proj=Path(__file__).resolve().parent
    entry=proj / "main_plus.py"

    os.makedirs(args.results_dir, exist_ok=True)
    boards=sorted([f for f in os.listdir(args.boards_dir) if f.endswith(".bff")])

    combos=[("wall","v2"),("wall","parallel"),("center","v2"),("center","parallel")]
    rows=[]
    for name in boards:
        bff_path=os.path.join(args.boards_dir, name)
        for collision, solver in combos:
            cmd=[sys.executable, str(entry), bff_path,
                 "--collision", collision, "--solver", solver,
                 "--time_limit", str(args.time_limit), "--png", str(args.png),
                 "--seed", str(args.seed), "--workers", str(args.workers),
                 "--out", args.results_dir, "--results_dir", args.results_dir]
            print("[RUN]", " ".join(shlex.quote(c) for c in cmd))
            try:
                out=subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                msg=out.decode("utf-8", errors="ignore").strip().splitlines()[-1]
            except subprocess.CalledProcessError as e:
                msg=e.output.decode("utf-8", errors="ignore").strip().splitlines()[-1] if e.output else str(e)
            rows.append([name, collision, solver, args.time_limit, args.png, args.seed, args.workers, msg])

    csvp=os.path.join(args.results_dir, "summary_unified.csv")
    with open(csvp,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["board","collision","solver","time_limit","png","seed","workers","message"])
        for r in rows: w.writerow(r)
    print("[OK] Comparison written:", csvp)

if __name__=="__main__": main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, subprocess, shlex, csv, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--boards_dir", default="boards")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--png", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--results_dir", default="results")
    args=ap.parse_args()

    proj=Path(__file__).resolve().parent
    entry=proj / "main_unified.py"

    os.makedirs(args.results_dir, exist_ok=True)
    boards=sorted([f for f in os.listdir(args.boards_dir) if f.endswith(".bff")])

    csvp=Path(args.results_dir)/"summary_wall.csv"
    with open(csvp,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["board","collision","solver","time","message"])
        for name in boards:
            bff_path=os.path.join(args.boards_dir, name)
            cmd=[sys.executable, str(entry), bff_path, "--collision","wall",
                 "--time_limit", str(args.time_limit), "--png", str(args.png), "--seed", str(args.seed),
                 "--out", args.results_dir]
            print("[RUN]", " ".join(shlex.quote(c) for c in cmd))
            try:
                out=subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                msg=out.decode("utf-8", errors="ignore").strip()
            except subprocess.CalledProcessError as e:
                msg=e.output.decode("utf-8", errors="ignore").strip()
            w.writerow([name,"wall","v2", f"{args.time_limit:.0f}", msg])
    print("[OK] Comparison written:", csvp)

if __name__=="__main__": main()

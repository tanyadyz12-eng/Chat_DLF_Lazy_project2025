#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: CLI entry point: parse arguments, invoke solver, render and write artifacts.
• Inputs: Command-line arguments (bff path, solver, collision, etc.)
• Outputs: Artifacts in results (.txt/.json/(optional) image)
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
import argparse
import time
from pathlib import Path
from bff_parser import parse_bff
from solver_v2 import solve as solve_v2
from solver_parallel import solve_parallel
from simulate import trace as trace_center
from simulate_wall import trace as trace_wall
from render_plus import save_all


def main():
    """Main function: parse arguments, solve map, save results.
    
    Parses command line arguments, reads .bff file, runs solver, and generates output files.
    """
    ap=argparse.ArgumentParser()
    ap.add_argument("bff_file")
    ap.add_argument("--collision", choices=["center","wall"], default="wall")
    ap.add_argument("--solver", choices=["v2","parallel"], default="v2")
    ap.add_argument("--time_limit", type=float, default=120.0)
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--out", type=str, default="outputs")
    ap.add_argument("--results_dir", type=str, default="results")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=4)
    args=ap.parse_args()

    board=parse_bff(args.bff_file)
    tracer=trace_wall if args.collision=="wall" else trace_center

    t0=time.time()
    if args.solver=="v2":
        sol=solve_v2(board, time_limit=args.time_limit, seed=args.seed, tracer=tracer)
    else:
        res=solve_parallel(board, wallclock_limit=args.time_limit, workers=args.workers,
                           tracer_name=("wall" if args.collision=="wall" else "center"))
        sol=res.placements
    elapsed=time.time()-t0

    hits,traj=tracer(board, sol or {})
    base=Path(args.bff_file).stem+f"_{args.collision}_{args.solver}"
    save_all(args.out, base, board, sol or {}, hits, traj, elapsed,
             seed=args.seed, collision=args.collision, solver=args.solver, png=args.png, write_json=1)
    print(f"[OK] {args.collision}/{args.solver} in {elapsed:.3f}s → {args.out}/{base}.txt")

if __name__=="__main__": main()

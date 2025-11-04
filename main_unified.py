#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, time
from pathlib import Path
from bff_parser import parse_bff
from solver_v2 import solve as solve_v2
from simulate import trace as trace_center
from simulate_wall import trace as trace_wall
from render_plus import save_all

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("bff_file")
    ap.add_argument("--collision", choices=["center","wall"], default="wall")
    ap.add_argument("--time_limit", type=float, default=120.0)
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--out", type=str, default="outputs")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--json", type=int, default=1)
    args=ap.parse_args()

    board=parse_bff(args.bff_file)
    tracer=trace_wall if args.collision=="wall" else trace_center

    t0=time.time()
    sol=solve_v2(board, time_limit=args.time_limit, seed=args.seed, tracer=tracer)
    elapsed=time.time()-t0

    hits,traj=tracer(board, sol or {})
    base=Path(args.bff_file).stem+f"_{args.collision}_v2"
    save_all(args.out, base, board, sol or {}, hits, traj, elapsed,
             seed=args.seed, collision=args.collision, solver="v2", png=args.png, write_json=args.json)
    print(f"[OK] {args.collision}/v2 in {elapsed:.3f}s → {args.out}/{base}.txt")

if __name__=="__main__": main()

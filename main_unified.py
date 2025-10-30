
"""
main_unified.py
Unified entry with --collision center|wall (default wall) and rich output.
"""
from __future__ import annotations
import argparse, time, os
from bff_parser import parse_bff
from model import build_board
from solver_v2 import solve as solve_v2
from simulate import trace as trace_center
from simulate_wall import trace as trace_wall
from render_plus import save_text_with_header, save_png_plus

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bff", help="Path to .bff file")
    ap.add_argument("--collision", choices=["center","wall"], default="wall")
    ap.add_argument("--time_limit", type=float, default=180.0)
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--results_dir", default="results")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    parsed = parse_bff(args.bff)
    board = build_board(parsed)
    tracer = trace_wall if args.collision == "wall" else trace_center

    t0 = time.time()
    sol = solve_v2(board, time_limit=args.time_limit, seed=args.seed)
    elapsed = time.time() - t0

    name = os.path.splitext(os.path.basename(args.bff))[0]
    suffix = f"{args.collision}"
    out_txt = os.path.join(args.results_dir, f"{name}_solution_{suffix}.txt")

    if sol is None:
        hits, traj = tracer(board, {})
        save_text_with_header(out_txt, board, {}, hits, elapsed, collision=args.collision)
        if args.png:
            out_png = os.path.join(args.results_dir, f"{name}_paths_{suffix}.png")
            save_png_plus(out_png, board, {}, traj, hits, collision=args.collision)
        print(f"[WARN] ({args.collision}) No solution within time limit. Report saved to {out_txt}")
        return

    hits, traj = tracer(board, sol)
    save_text_with_header(out_txt, board, sol, hits, elapsed, collision=args.collision)
    print(f"[OK] ({args.collision}) Solution in {elapsed:.2f}s. Saved to {out_txt}")
    if args.png:
        out_png = os.path.join(args.results_dir, f"{name}_solution_{suffix}.png")
        save_png_plus(out_png, board, sol, traj, hits, collision=args.collision)

if __name__ == "__main__":
    main()

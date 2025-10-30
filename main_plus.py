
"""
main_plus.py
Drop-in main that adds --solver {v2,parallel} on top of main_unified features.
Default solver is "parallel" for better robustness.
"""
from __future__ import annotations
import argparse, time, os
from bff_parser import parse_bff
from model import build_board
from solver_v2 import solve as solve_v2
from solver_parallel import solve_parallel
from simulate import trace as trace_center
from simulate_wall import trace as trace_wall
from render_plus import save_text_with_header, save_png_plus

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bff", help="Path to .bff file")
    ap.add_argument("--collision", choices=["center","wall"], default="wall")
    ap.add_argument("--solver", choices=["v2","parallel"], default="parallel")
    ap.add_argument("--time_limit", type=float, default=180.0, help="Total wall-clock (parallel) or single-run (v2)")
    ap.add_argument("--png", type=int, default=1)
    ap.add_argument("--results_dir", default="results")
    ap.add_argument("--seed", type=int, default=0, help="Used by solver v2 only")
    ap.add_argument("--workers", type=int, default=0, help="parallel solver workers (0 = auto)")
    args = ap.parse_args()

    parsed = parse_bff(args.bff)
    board = build_board(parsed)
    tracer = trace_wall if args.collision == "wall" else trace_center

    t0 = time.time()
    if args.solver == "v2":
        sol = solve_v2(board, time_limit=args.time_limit, seed=args.seed)
    else:
        sol = solve_parallel(board, wallclock_limit=args.time_limit, workers=args.workers)
    elapsed = time.time() - t0

    name = os.path.splitext(os.path.basename(args.bff))[0]
    suffix = f"{args.collision}_{args.solver}"
    out_txt = os.path.join(args.results_dir, f"{name}_solution_{suffix}.txt")

    if sol is None:
        hits, traj = tracer(board, {})
        save_text_with_header(out_txt, board, {}, hits, elapsed, collision=f"{args.collision} / {args.solver}")
        if args.png:
            out_png = os.path.join(args.results_dir, f"{name}_paths_{suffix}.png")
            save_png_plus(out_png, board, {}, traj, hits, collision=f"{args.collision} / {args.solver}")
        print(f"[WARN] ({args.collision}/{args.solver}) No solution within time limit. Report saved to {out_txt}")
        return

    hits, traj = tracer(board, sol)
    save_text_with_header(out_txt, board, sol, hits, elapsed, collision=f"{args.collision} / {args.solver}")
    print(f"[OK] ({args.collision}/{args.solver}) Solution in {elapsed:.2f}s. Saved to {out_txt}")
    if args.png:
        out_png = os.path.join(args.results_dir, f"{name}_solution_{suffix}.png")
        save_png_plus(out_png, board, sol, traj, hits, collision=f"{args.collision} / {args.solver}")

if __name__ == "__main__":
    main()

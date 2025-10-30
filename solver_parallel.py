
"""
solver_parallel.py
Parallel meta-solver that runs solver_v2 with multiple random seeds
in parallel worker processes. Returns the first feasible placement.
Also supports a "best effort" mode that keeps the best partial
(number of targets hit) if time expires.
"""
from __future__ import annotations
from typing import Dict, Tuple, Optional, List, Set
from dataclasses import dataclass
import multiprocessing as mp
import time as _time

from model import Board, Block, BlockType
from solver_v2 import solve as solve_v2
from simulate import trace as trace_center

@dataclass
class Result:
    placements: Optional[Dict[Tuple[int,int], Block]]
    hits: int
    seed: int
    elapsed: float

def _worker_run(board_data, time_budget: float, seed: int, return_hits: bool) -> Result:
    # reconstruct a Board: board_data is a shallow-serializable dict
    from model import Board, Block, BlockType, Laser
    import copy
    B: Board = copy.deepcopy(board_data)  # board_data is actually a Board instance (copy ok)
    t0 = _time.time()
    sol = solve_v2(B, time_limit=time_budget, seed=seed)
    elapsed = _time.time() - t0
    if sol is not None and return_hits:
        hit, _ = trace_center(B, sol)
        return Result(sol, len(hit), seed, elapsed)
    elif sol is not None:
        return Result(sol, 10**9, seed, elapsed)  # large sentinel
    else:
        if return_hits:
            hit, _ = trace_center(B, {})
            return Result(None, len(hit), seed, elapsed)
        else:
            return Result(None, 0, seed, elapsed)

def solve_parallel(board: Board,
                   wallclock_limit: float = 180.0,
                   seeds: Optional[List[int]] = None,
                   workers: int = 0,
                   return_best_effort: bool = True) -> Optional[Dict[Tuple[int,int], Block]]:
    """
    Run multiple solver_v2 attempts with different seeds in parallel.
    - wallclock_limit: total time budget for the whole meta-solver.
    - seeds: if None, use a default diversified list.
    - workers: 0 -> mp.cpu_count(), else the specified number.
    - return_best_effort: if True, return the placement that yields the
      highest #hits (using center trace) when time runs out (may be None).
    """
    import copy
    if seeds is None:
        seeds = [0,1,2,3,5,7,11,13,17,19,23,29]
    if workers <= 0:
        workers = min(len(seeds), max(1, mp.cpu_count() - 1))

    # Split time budget fairly among attempts; add a small overhead margin.
    per_job = max(5.0, 0.85 * wallclock_limit / len(seeds))

    best: Optional[Result] = None
    start = _time.time()

    # Because Board contains class instances, we pass a deepcopy to each worker
    B_data = copy.deepcopy(board)

    with mp.Pool(processes=workers) as pool:
        jobs = []
        for sd in seeds:
            jobs.append(pool.apply_async(_worker_run, (B_data, per_job, sd, True)))

        for j in jobs:
            remaining = wallclock_limit - (time.time() - start)
            try:
                res: Result = j.get(timeout=max(1.0, remaining))
            except Exception:
                continue
            if res.placements is not None:
                # found a valid solution -> early stop
                pool.terminate()
                pool.join()
                return res.placements
            # track best effort
            if return_best_effort:
                if best is None or res.hits > best.hits:
                    best = res
            if (time.time() - start) > wallclock_limit:
                break

    # no exact solution; return best effort (may be None)
    if return_best_effort and best is not None:
        return best.placements  # likely None, but API stays consistent
    return None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Tuple, Optional, List, Set
from dataclasses import dataclass
import multiprocessing as mp, time as _time, copy
from model import Board, Block
from solver_v2 import solve as solve_v2

@dataclass
class Result:
    placements: Optional[Dict[Tuple[int, int], Block]]
    hits: int
    seed: int
    elapsed: float

def _worker_run(board_data: Board, time_budget: float, seed: int, tracer_name: str) -> Result:
    B = copy.deepcopy(board_data); t0=_time.time()
    if tracer_name=='wall':
        from simulate_wall import trace as tracer
    else:
        from simulate import trace as tracer
    sol = solve_v2(B, time_limit=time_budget, seed=seed, tracer=tracer)
    elapsed=_time.time()-t0
    hits=0
    try: hits=len(tracer(B, sol or {})[0])
    except Exception: pass
    return Result(sol, hits, seed, elapsed)

def solve_parallel(board: Board, wallclock_limit: float = 120, workers: int = 4, tracer_name: str = 'center') -> Result:
    start=_time.time(); best:Optional[Result]=None; n=max(1,int(workers))
    ctx=mp.get_context("spawn")
    with ctx.Pool(processes=n) as pool:
        inflight=[]; cap=max(2*n,4); seed_base=int(_time.time()*1e6)%2_147_483_647
        try:
            while True:
                rem=wallclock_limit-(_time.time()-start)
                if rem<=0: break
                while len(inflight)<cap and rem>0:
                    budget=max(1.0, min(rem, wallclock_limit/3.0))
                    seed=seed_base+len(inflight)
                    inflight.append(pool.apply_async(_worker_run,(board,budget,seed,tracer_name)))
                    rem=wallclock_limit-(_time.time()-start)
                i=0
                while i<len(inflight):
                    a=inflight[i]
                    if a.ready():
                        try: res=a.get()
                        except Exception: inflight.pop(i); continue
                        if res.placements:
                            pool.terminate(); pool.join(); return res
                        if (best is None) or (res.hits>best.hits): best=res
                        inflight.pop(i); continue
                    i+=1
        finally:
            try: pool.terminate(); pool.join()
            except Exception: pass
    total=_time.time()-start
    if best is not None: best.elapsed=total; return best
    return Result(None,0,seed_base,total)

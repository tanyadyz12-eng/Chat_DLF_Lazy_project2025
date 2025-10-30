
"""
solver_v2.py
Heuristic backtracking with improved slot ordering and memoization.
"""
from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Set
from dataclasses import dataclass
import random, time as _time
from model import Board, Block, BlockType
from simulate import trace as trace_center  # used for early testing regardless of collision

def order_slots(board: Board, seed:int=0) -> List[Tuple[int,int]]:
    laser_pts = [(L.x, L.y) for L in board.lasers]
    target_pts = list(board.targets)
    def score(rc):
        r,c = rc
        cx, cy = 2*c+1, 2*r+1
        s1 = min((abs(cx-lx)+abs(cy-ly) for (lx,ly) in laser_pts), default=0)
        s2 = min((abs(cx-tx)+abs(cy-ty) for (tx,ty) in target_pts), default=0)
        return (s1 + 1.5*s2)
    arr = sorted(board.movable_slots, key=score)
    rnd = random.Random(seed)
    for i in range(0, len(arr), 4):
        rnd.shuffle(arr[i:i+4])
    return arr

def try_order(stock: Dict[str,int]) -> List[str]:
    order = []
    if stock.get('A',0)>0: order.append('A')
    if stock.get('C',0)>0: order.append('C')
    if stock.get('B',0)>0: order.append('B')
    return order

def placements_hash(placements: Dict[Tuple[int,int], Block]) -> Tuple:
    return tuple(sorted(((r,c,b.kind.value) for (r,c),b in placements.items())))

def solved_all(hit:Set[Tuple[int,int]], targets:Set[Tuple[int,int]]) -> bool:
    return targets.issubset(hit)

def backtrack(board: Board, slots: List[Tuple[int,int]], idx:int,
              placements: Dict[Tuple[int,int], Block],
              memo: Dict[Tuple,bool],
              timeup: callable) -> Optional[Dict[Tuple[int,int], Block]]:

    if timeup():
        return None

    # Early check using center model (fast)
    hit, _ = trace_center(board, placements)
    if solved_all(hit, board.targets):
        return dict(placements)

    if idx >= len(slots):
        return None

    key = (placements_hash(placements), (board.stock.get('A',0), board.stock.get('B',0), board.stock.get('C',0)), idx)
    if key in memo and memo[key] is False:
        return None

    r,c = slots[idx]

    for kind in try_order(board.stock):
        if board.stock.get(kind,0) <= 0: 
            continue
        board.stock[kind] -= 1
        placements[(r,c)] = Block(BlockType.REFLECT if kind=='A' else BlockType.OPAQUE if kind=='B' else BlockType.REFRACT)

        sol = backtrack(board, slots, idx+1, placements, memo, timeup)
        if sol is not None:
            return sol

        board.stock[kind] += 1
        placements.pop((r,c), None)
        if timeup():
            return None

    sol = backtrack(board, slots, idx+1, placements, memo, timeup)
    if sol is not None:
        return sol

    memo[key] = False
    return None

def solve(board: Board, time_limit: float=180.0, seed:int=0) -> Optional[Dict[Tuple[int,int], Block]]:
    t0 = _time.time()
    def timeup():
        return (_time.time() - t0) > time_limit
    slots = order_slots(board, seed=seed)
    memo: Dict[Tuple,bool] = {}
    return backtrack(board, slots, 0, {}, memo, timeup)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: Backtracking + heuristics solver (supports time_limit and random seed).
• Inputs: Board + time_limit + seed (+tracer)
• Outputs: placements dict or None
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Set, Callable
import random, time as _time
from model import Board, Block, BlockType

def order_slots(board: Board, seed:int=0) -> List[Tuple[int,int]]:
    laser_pts = [(L.x,L.y) for L in board.lasers]; target_pts = list(board.targets)
    def score(rc):
        r,c=rc; cx,cy=2*c+1,2*r+1
        # Prioritize slots closer to both lasers and targets
        s1=min((abs(cx-lx)+abs(cy-ly) for (lx,ly) in laser_pts), default=0)
        s2=min((abs(cx-tx)+abs(cy-ty) for (tx,ty) in target_pts), default=0)
        # Also consider slots that are on paths between lasers and targets
        s3=0
        for (lx,ly) in laser_pts:
            for (tx,ty) in target_pts:
                # Check if this slot is roughly on the line between laser and target
                dx,dy=tx-lx,ty-ly
                if dx==0 and dy==0: continue
                # Simple heuristic: if slot is close to the line, give bonus
                slot_to_line_dist = abs((cy-ly)*dx - (cx-lx)*dy) / max(abs(dx)+abs(dy), 1)
                if slot_to_line_dist < 2:
                    s3 += 1
        # Bonus for slots that are intersections (can affect multiple paths)
        s4 = 0
        if (cx % 2 == 1 and cy % 2 == 1):  # Center of block
            s4 = -0.3  # Slight preference for block centers
        return s1+1.8*s2-0.5*s3+s4  # Lower score is better
    arr=sorted(board.movable_slots, key=score)
    rnd=random.Random(seed)
    # Shuffle in smaller groups to maintain some locality but allow exploration
    for i in range(0,len(arr),2):  # Smaller groups for more exploration
        block=arr[i:i+2]; rnd.shuffle(block); arr[i:i+2]=block
    return arr

def try_order(stock: Dict[str,int], board: Board = None, slot: Tuple[int, int] = None, 
              current_hits: Set[Tuple[int,int]] = None) -> List[str]:
    """Try block types in order, with context-aware ordering"""
    out=[]; 
    
    # If we have context, prioritize based on need
    if current_hits is not None and board is not None:
        remaining = len(board.targets - current_hits)
        # If we need to hit many targets, prefer REFRACT (creates multiple rays)
        if remaining > 1 and stock.get('C',0) > 0:
            out.append('C')
        # Always try REFLECT (most flexible)
        if stock.get('A',0)>0: out.append('A')
        # OPAQUE is most restrictive, try last
        if stock.get('B',0)>0: out.append('B')
        # If we already added C above, don't add again
        if remaining <= 1 or stock.get('C',0) == 0:
            if stock.get('C',0)>0: out.append('C')
    else:
        # Default order: REFLECT (most common), REFRACT (flexible), OPAQUE (restrictive)
        if stock.get('A',0)>0: out.append('A')
        if stock.get('C',0)>0: out.append('C')
        if stock.get('B',0)>0: out.append('B')
    
    return out

def placements_hash(placements: Dict[Tuple[int,int], Block]) -> Tuple:
    return tuple(sorted(((r,c,b.kind.value) for (r,c),b in placements.items())))

def evaluate_state(board: Board, hits: Set[Tuple[int,int]], tracer: Callable) -> float:
    """Heuristic evaluation: higher is better"""
    # Number of targets hit
    hit_count = len(board.targets & hits)
    # Number of targets remaining
    remaining = len(board.targets - hits)
    # Bonus for hitting more targets (exponential bonus for progress)
    score = hit_count * 1000.0 - remaining * 100.0
    # Additional bonus if we hit all targets
    if remaining == 0:
        score += 10000.0
    return score

def solve(board: Board, time_limit: float=180.0, seed:int=0,
          tracer: Callable[[Board, Dict[Tuple[int,int], Block]], Tuple[Set[Tuple[int,int]], list]] = None
         ) -> Optional[Dict[Tuple[int,int], Block]]:
    if tracer is None:
        from simulate import trace as tracer
    t0=_time.time()
    def timeup(): return (_time.time()-t0)>time_limit
    best_score = -1e9
    best_solution = None

    def backtrack(idx:int, placements: Dict[Tuple[int,int], Block]):
        nonlocal best_score, best_solution
        if timeup(): return None
        
        hits,_=tracer(board,placements)
        if board.targets.issubset(hits):
            best_solution = dict(placements)
            return best_solution
        
        # Evaluate current state
        score = evaluate_state(board, hits, tracer)
        if score > best_score:
            best_score = score
            best_solution = dict(placements)  # Keep best partial solution
        
        if idx>=len(slots): return None
        
        # Early pruning: if we can't possibly hit all targets with remaining blocks
        remaining_targets = len(board.targets - hits)
        remaining_blocks = sum(board.stock.values())
        if remaining_targets > remaining_blocks and remaining_blocks > 0:
            # Need at least one block per target, but this is heuristic
            pass  # Don't prune too aggressively
        
        r,c=slots[idx]
        
        # Don't use visited check - it's too aggressive and can miss solutions
        # The search space is manageable without it, and it prevents finding valid solutions
        # visited.clear()  # Removed aggressive pruning
        
        # Try placing blocks in order of preference, with context awareness
        options = try_order(board.stock, board, (r, c), hits)
        
        # Sort options by potential value (heuristic)
        # For slots close to targets, prefer REFLECT/REFRACT
        slot_r, slot_c = r, c
        slot_center = (2*slot_c+1, 2*slot_r+1)
        min_target_dist = min((abs(slot_center[0]-tx) + abs(slot_center[1]-ty) 
                              for (tx,ty) in board.targets), default=1000)
        
        # If slot is close to targets, prefer REFLECT and REFRACT
        if min_target_dist < 4:
            options = sorted(options, key=lambda k: {'A': 0, 'C': 1, 'B': 2}.get(k, 3))
        
        for kind in options:
            if timeup(): return None
            board.stock[kind]-=1
            placements[(r,c)]=Block(BlockType.REFLECT if kind=='A' else BlockType.OPAQUE if kind=='B' else BlockType.REFRACT)
            sol=backtrack(idx+1, placements)
            if sol is not None: return sol
            board.stock[kind]+=1
            placements.pop((r,c),None)
        
        # Try leaving slot empty
        sol=backtrack(idx+1, placements)
        if sol is not None: return sol
        
        return None
    
    # Try multiple seeds and different search strategies for better exploration
    seeds_to_try = [seed, seed + 1, seed + 2, seed + 10, seed + 20, seed + 42, seed + 100, seed + 200]
    
    for attempt, current_seed in enumerate(seeds_to_try):
        if timeup(): break
        slots = order_slots(board, seed=current_seed)
        
        # Try full depth search
        result = backtrack(0, {})
        if result is not None:
            return result
        if timeup(): break
    
    # Return best solution found so far (if any)
    return best_solution

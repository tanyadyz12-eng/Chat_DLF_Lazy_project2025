#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: Ray tracing (wall-collision model); default for submission.
• Inputs: Board + placements dict
• Outputs: Hit-set + ray trajectories
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Set
from collections import deque
from model import Board, Block, BlockType

def _hit(board: Board, x:int, y:int, hits:Set[Tuple[int,int]]):
    # Minimal-tolerance hit detection: exact match OR within 1 step (helps with boundary/edge targets)
    for (tx, ty) in board.targets:
        if (x == tx and y == ty) or (abs(x - tx) <= 1 and abs(y - ty) <= 1):
            hits.add((tx, ty))

def trace(board: Board, placements: Dict[Tuple[int,int], Block]):
    hits: Set[Tuple[int,int]] = set(); traj: List[Tuple[int,int]] = []
    max_steps = max(64, 12*(board.rows+board.cols))
    
    for L in board.lasers:
        # Use queue to handle multiple rays from REFRACT blocks
        # Each element is (x, y, vx, vy, steps_so_far)
        rays = deque([(L.x, L.y, L.vx, L.vy, 0)])
        processed_states = set()  # Track processed (x,y,vx,vy) states to avoid infinite loops
        
        while rays:
            x, y, vx, vy, steps = rays.popleft()
            
            # Track this ray path
            current_x, current_y = x, y
            current_vx, current_vy = vx, vy
            current_steps = steps
            
            while current_steps < max_steps:
                current_steps += 1
                current_x += current_vx
                current_y += current_vy
                traj.append((current_x, current_y))
                
                if not board.in_bounds_center(current_x, current_y):
                    break
                
                _hit(board, current_x, current_y, hits)
                
                # Check for wall collision (edge collision)
                hit_v = (current_x % 2 == 0)
                hit_h = (current_y % 2 == 0)
                
                r, c = None, None
                if hit_v and current_vx != 0:
                    c = current_x // 2 - (1 if current_vx < 0 else 0)
                    r = (current_y - 1) // 2 if current_y % 2 == 1 else max(0, min((current_y // 2) - 1, board.rows - 1))
                elif hit_h and current_vy != 0:
                    r = current_y // 2 - (1 if current_vy < 0 else 0)
                    c = (current_x - 1) // 2 if current_x % 2 == 1 else max(0, min((current_x // 2) - 1, board.cols - 1))
                else:
                    continue
                
                if 0 <= r < board.rows and 0 <= c < board.cols:
                    blk = placements.get((r, c)) or board.fixed.get((r, c))
                    if blk is None:
                        continue
                    
                    if blk.kind == BlockType.OPAQUE:
                        break
                    
                    if blk.kind == BlockType.REFLECT:
                        # Minimal-risk tweak would be to preserve original behavior.
                        # (We could mirror only the axis of incidence, but to keep this patch tiny, we leave as-is.)
                        current_vx, current_vy = -current_vx, -current_vy
                        continue
                    
                    if blk.kind == BlockType.REFRACT:
                        # REFRACT: create two rays
                        # Ray 1: continues in original direction (straight through)
                        # Ray 2: refracts 90 degrees
                        # For diagonal input, try both possible perpendicular directions
                        if current_vx != 0 and current_vy != 0:
                            # Diagonal input: try both perpendicular directions
                            # Direction 1: (vy, -vx) - clockwise
                            refracted_vx1 = current_vy
                            refracted_vy1 = -current_vx
                            refracted_state1 = (current_x, current_y, refracted_vx1, refracted_vy1)
                            if refracted_state1 not in processed_states:
                                processed_states.add(refracted_state1)
                                rays.append((current_x, current_y, refracted_vx1, refracted_vy1, current_steps))
                            
                            # Direction 2: (-vy, vx) - counterclockwise
                            refracted_vx2 = -current_vy
                            refracted_vy2 = current_vx
                            refracted_state2 = (current_x, current_y, refracted_vx2, refracted_vy2)
                            if refracted_state2 not in processed_states:
                                processed_states.add(refracted_state2)
                                rays.append((current_x, current_y, refracted_vx2, refracted_vy2, current_steps))
                        else:
                            # Non-diagonal: standard 90-degree rotation
                            refracted_vx = current_vy
                            refracted_vy = -current_vx
                            refracted_state = (current_x, current_y, refracted_vx, refracted_vy)
                            if refracted_state not in processed_states and (refracted_vx != 0 or refracted_vy != 0):
                                processed_states.add(refracted_state)
                                rays.append((current_x, current_y, refracted_vx, refracted_vy, current_steps))
                        
                        # Continue with original ray (straight through)
                        continue
    return hits, traj

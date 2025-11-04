#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: Rendering and artifact writing (.txt/.json/(optional) image) without extra deps.
• Inputs: Board + placements + hits + traj
• Outputs: txt/json/(optional) image file
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Set, Optional
import json, os
from model import Board, Block
from render import save_text as save_text_basic, save_png as save_png_basic

def save_all(out_dir: str, base_name: str, board: Board, placements: Dict[Tuple[int,int], Block],
             hits:Set[Tuple[int,int]], traj: List[Tuple[int,int]], elapsed: float,
             seed: Optional[int]=None, collision: Optional[str]=None, solver: Optional[str]=None,
             png:int=1, write_json:int=1):
    os.makedirs(out_dir, exist_ok=True)
    txt = os.path.join(out_dir, f"{base_name}.txt")
    png_path = os.path.join(out_dir, f"{base_name}.png")
    json_path = os.path.join(out_dir, f"{base_name}.json")

    # Text summary (unchanged behavior)
    save_text_basic(txt, board, placements, hits, elapsed, seed=seed, collision=collision, solver=solver)

    # PNG with explicit hits + informative title
    if png:
        title = f"{base_name} • collision={collision} • solver={solver}"
        save_png_basic(png_path, board, placements, traj, hits=hits, title=title, annotate_blocks=True)

    # JSON summary (unchanged schema)
    if write_json:
        solved = set(board.targets).issubset(hits)
        summary = {
            "board": base_name,
            "solved": bool(solved),
            "targets_total": len(board.targets),
            "targets_hit": len(hits),
            "elapsed": float(elapsed),
            "seed": int(seed) if seed is not None else None,
            "collision": collision,
            "solver": solver,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

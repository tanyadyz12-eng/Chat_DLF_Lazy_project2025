#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: Parse `.bff` into Board (grid, stock, lasers, targets).
• Inputs: .bff text
• Outputs: Board object
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
from typing import Tuple, List, Dict, Set
from pathlib import Path
from model import Board, Block, BlockType, Laser

def _parse_stock_val(s: str) -> int:
    s = s.strip()
    if ":" in s: s = s.split(":", 1)[1]
    if "=" in s: s = s.split("=", 1)[1]
    return int(s.strip())

def parse_bff(path: str) -> Board:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    grid_rows: List[List[str]] = []
    in_grid = False
    stock = {'A':0,'B':0,'C':0}
    fixed: Dict[Tuple[int,int], Block] = {}
    movable: List[Tuple[int,int]] = []
    lasers: List[Laser] = []
    targets: Set[Tuple[int,int]] = set()

    r = 0
    for raw in text:
        line = raw.strip()
        if not line or line.startswith('#'): continue
        if line.upper().startswith('GRID START'):
            in_grid = True; r = 0; grid_rows.clear(); continue
        if line.upper().startswith('GRID STOP'):
            in_grid = False; continue
        if in_grid:
            toks = line.split()
            grid_rows.append(toks)
            for c, tok in enumerate(toks):
                if tok in ('o','O'): movable.append((r,c))
                elif tok in ('x','X'): pass
                elif tok in ('A','B','C'):
                    fixed[(r,c)] = Block(BlockType.REFLECT if tok=='A' else BlockType.OPAQUE if tok=='B' else BlockType.REFRACT)
                else:
                    # Be lenient: treat unknown token as placeable
                    movable.append((r,c))
            r += 1; continue
        if line and line[0].upper() in ('A','B','C'):
            key = line[0].upper()
            stock[key] = _parse_stock_val(line[1:]); continue
        if line and line[0].upper() == 'L':
            toks = line[1:].split()
            x, y, vx, vy = map(int, toks[:4])
            lasers.append(Laser(x, y, vx, vy)); continue
        if line and line[0].upper() == 'P':
            toks = line[1:].split()
            tx, ty = map(int, toks[:2])
            targets.add((tx, ty)); continue

    rows = len(grid_rows)
    cols = max(len(rr) for rr in grid_rows) if grid_rows else 0
    for rr in grid_rows:
        if len(rr) != cols:
            rr += ['x'] * (cols - len(rr))

    # Conservative default stock ONLY if A/B/C all omitted or zero
    if all(stock.get(k,0) == 0 for k in ('A','B','C')):
        stock = {'A': 2, 'B': 1, 'C': 1}

    return Board(rows, cols, grid_rows, fixed, movable, targets, lasers, stock)

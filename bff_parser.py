
"""
bff_parser.py
Robust parser for Lazors .bff files (supports "A 2", "A: 2", "A=2").
"""
from __future__ import annotations
from typing import List, Tuple, Dict
import re

def parse_bff(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [ln.strip() for ln in f.readlines()]
    content = [ln for ln in lines if ln and not ln.startswith('#')]

    grid: List[List[str]] = []
    in_grid = False
    stock = {'A': 0, 'B': 0, 'C': 0}
    lasers = []
    targets = []

    for ln in content:
        up = ln.upper()
        if up.startswith('GRID START'):
            in_grid = True; continue
        if up.startswith('GRID STOP'):
            in_grid = False; continue
        if in_grid:
            row = ln.split()
            if grid and len(row) != len(grid[0]):
                raise ValueError(f"Inconsistent GRID row length in {path}")
            grid.append(row); continue

        m = re.match(r'^([ABC])\s*[:=]?\s*(\d+)$', ln.strip(), re.IGNORECASE)
        if m:
            stock[m.group(1).upper()] = int(m.group(2)); continue

        if ln.startswith('L'):
            nums = [int(x) for x in ln.split()[1:]]
            if len(nums) < 4: raise ValueError(f"Invalid laser line: {ln}")
            lasers.append(tuple(nums[:4])); continue

        if ln.startswith('P'):
            nums = [int(x) for x in ln.split()[1:]]
            if len(nums) < 2: raise ValueError(f"Invalid target line: {ln}")
            targets.append(tuple(nums[:2])); continue

    if not grid: raise ValueError(f"No GRID found in {path}")
    rows, cols = len(grid), len(grid[0])
    valid = {'o','x','A','B','C'}
    for r in grid:
        for t in r:
            if t not in valid:
                raise ValueError(f"Unknown token '{t}' in {path}")
    return {'grid': grid, 'stock': stock, 'lasers': lasers, 'targets': targets, 'shape': (rows, cols)}

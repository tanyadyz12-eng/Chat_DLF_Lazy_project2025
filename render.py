#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced render.py (auto-infer hits if not provided)

Why this file:
- Some callers (older render_plus.py) call save_png(...) without the 'hits' arg.
- To keep orange "Hit" markers visible, we infer hits from the trajectory
  by intersecting the path points with target coordinates.

Features:
- Clear legend: Laser path / Target / Hit / Missed target / Blocks
- Distinct markers & colors
- Reflection point labels (R1, R2, ...), auto-detected from direction changes
- Block coordinates annotated
- Informative title (pass via render_plus.save_all if available)
"""
from __future__ import annotations
from typing import Dict, Tuple, List, Set, Optional
from model import Board, Block
import os

# ---------- ASCII text helpers ----------
def ascii_board(board: Board, placements: Dict[Tuple[int,int], Block]) -> str:
    out = []
    for r in range(board.rows):
        row = []
        for c in range(board.cols):
            if (r,c) in board.fixed:
                row.append(board.fixed[(r,c)].kind.value)
            elif (r,c) in placements:
                row.append(placements[(r,c)].kind.value.lower())
            else:
                row.append(board.grid[r][c])
        out.append(" ".join(row))
    return "\n".join(out)

def save_text(path: str, board: Board, placements: Dict[Tuple[int,int], Block],
              hits:Set[Tuple[int,int]], elapsed: float, seed:int=None, collision:str=None, solver:str=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Solved: {set(board.targets).issubset(hits)}\n")
        f.write(f"Targets hit: {len(hits)} / {len(board.targets)}\n")
        if seed is not None: f.write(f"Seed: {seed}\n")
        if collision: f.write(f"Collision: {collision}\n")
        if solver: f.write(f"Solver: {solver}\n")
        f.write(f"Time: {elapsed:.3f} s\n\n")
        f.write("Board (lowercase = placed block):\n")
        f.write(ascii_board(board, placements)); f.write("\n")

# ---------- PNG visualization ----------
def _detect_reflections(traj: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    """Return a list of corner points where the direction changes."""
    if not traj or len(traj) < 3: 
        return []
    turns: List[Tuple[int,int]] = []
    for i in range(1, len(traj)-1):
        x0, y0 = traj[i-1]
        x1, y1 = traj[i]
        x2, y2 = traj[i+1]
        dx1, dy1 = x1-x0, y1-y0
        dx2, dy2 = x2-x1, y2-y1
        if (dx1, dy1) != (dx2, dy2):
            turns.append((x1,y1))
    # unique while preserving order
    seen = set(); uniq = []
    for p in turns:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq

def save_png(path: str,
             board: Board,
             placements: Dict[Tuple[int,int], Block],
             traj: List[Tuple[int,int]],
             hits: Optional[Set[Tuple[int,int]]] = None,
             title: Optional[str] = None,
             annotate_blocks: bool = True):
    """
    Enhanced visualization with legend, markers, and annotations.
    Auto-infers hits if not provided by caller.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # --- Auto-infer hits when arg missing ---
    if hits is None:
        traj_set = set(traj or [])
        hits = {t for t in board.targets if t in traj_set}

    fig, ax = plt.subplots(figsize=(6.8, 6.8))

    # 1) Draw background frame & grid
    ax.add_patch(plt.Rectangle((0,0), 2*board.cols, 2*board.rows,
                               fill=False, linewidth=2.0, alpha=0.8, zorder=0))
    for r in range(1, board.rows):
        y = 2*r
        ax.plot([0, 2*board.cols], [y, y], color="#999999", linewidth=0.8, alpha=0.6, zorder=0)
    for c in range(1, board.cols):
        x = 2*c
        ax.plot([x, x], [0, 2*board.rows], color="#999999", linewidth=0.8, alpha=0.6, zorder=0)

    # 2) Blocks (fixed + placements)
    block_colors = {'A':'#3B82F6', 'B':'#EF4444', 'C':'#10B981'}  # blue / red / green
    all_blocks = {**board.fixed, **placements}
    for (r,c), blk in all_blocks.items():
        x0, y0 = 2*c, 2*r
        rect = plt.Rectangle((x0, y0), 2, 2, color=block_colors[blk.kind.value], alpha=0.35, zorder=2)
        ax.add_patch(rect)
        ax.text(x0+1, y0+1, blk.kind.value, ha='center', va='center', fontsize=11, color='k', zorder=3)
        if annotate_blocks:
            ax.text(x0+0.15, y0+0.35, f"({r},{c})", ha='left', va='center', fontsize=8, color='#333333', zorder=3)

    # 3) Targets / Hits / Missed
    targets = list(board.targets)
    if targets:
        ax.plot([t[0] for t in targets], [t[1] for t in targets],
                marker='o', linestyle='None', ms=7, mfc='none', mec='#1D4ED8',
                label='Target', zorder=4)
    hits_list = list(hits) if hits else []
    if hits_list:
        ax.plot([h[0] for h in hits_list], [h[1] for h in hits_list],
                marker='*', linestyle='None', ms=11, mfc='#F59E0B', mec='#B45309',
                label='Hit', zorder=5)
    missed = [t for t in targets if t not in hits]
    if missed:
        ax.plot([m[0] for m in missed], [m[1] for m in missed],
                marker='x', linestyle='None', ms=8, mew=2, color='#DC2626',
                label='Missed target', zorder=5)

    # 4) Laser trajectory
    if traj:
        xs = [p[0] for p in traj]; ys = [p[1] for p in traj]
        ax.plot(xs, ys, '-', lw=2.0, label='Laser path', color='#16A34A', zorder=3, alpha=0.95)

        # Reflection labels at direction changes
        turns = _detect_reflections(traj)
        for i, (x, y) in enumerate(turns, start=1):
            ax.plot([x], [y], marker='s', ms=6, mfc='#111827', mec='white', zorder=6)
            ax.text(x+0.15, y-0.15, f"R{i}", fontsize=8, color='#111827',
                    ha='left', va='top', zorder=7)

    # 5) Cosmetics
    ax.set_aspect('equal')
    ax.set_xlim(-1, 2*board.cols+1)
    ax.set_ylim(-1, 2*board.rows+1)
    ax.invert_yaxis()
    ax.margins(0.02)
    if title:
        ax.set_title(title, fontsize=14, pad=10)
    leg = ax.legend(frameon=True, facecolor='#ffffff', framealpha=0.92, loc='upper right')
    for lh in getattr(leg, "legendHandles", []):
        try: lh.set_alpha(1.0)
        except Exception: pass

    ax.set_xlabel('x (doubled lattice)')
    ax.set_ylabel('y (doubled lattice)')
    import matplotlib.pyplot as plt
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close(fig)

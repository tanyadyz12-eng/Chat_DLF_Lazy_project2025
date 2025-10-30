
"""
render.py
Basic ASCII and PNG rendering (used as fallback).
"""
from __future__ import annotations
from typing import Dict, Tuple, List
from model import Board, Block
import os

def ascii_board(board: Board, placements: Dict[Tuple[int,int], Block]) -> str:
    rows, cols = board.rows, board.cols
    out = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if (r,c) in board.fixed:
                row.append(board.fixed[(r,c)].kind.value)
            elif (r,c) in placements:
                row.append(placements[(r,c)].kind.value.lower())
            else:
                row.append(board.grid[r][c])
        out.append(' '.join(row))
    return '\n'.join(out)

def save_text(path: str, board: Board, placements: Dict[Tuple[int,int], Block], hits, elapsed: float):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Solved: {set(board.targets).issubset(hits)}\n")
        f.write(f"Targets hit: {len(hits)} / {len(board.targets)}\n")
        f.write(f"Time: {elapsed:.3f} s\n\n")
        f.write("Board (lowercase = movable block placed):\n")
        f.write(ascii_board(board, placements))
        f.write("\n")

def save_png(path: str, board: Board, placements: Dict[Tuple[int,int], Block], traj: List[Tuple[int,int,int,int]]):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6,6))
    for r in range(board.rows):
        for c in range(board.cols):
            x0, y0 = 2*c, 2*r
            rect = plt.Rectangle((x0, y0), 2, 2, fill=False, linewidth=0.5)
            ax.add_patch(rect)
    for (r,c), blk in {**board.fixed, **placements}.items():
        x0, y0 = 2*c, 2*r
        color = {'A':'#4444aa','B':'#aa4444','C':'#44aa44'}[blk.kind.value]
        rect = plt.Rectangle((x0, y0), 2, 2, color=color, alpha=0.4)
        ax.add_patch(rect)
        ax.text(x0+1, y0+1, blk.kind.value, ha='center', va='center', fontsize=10, color='k')
    for (tx,ty) in board.targets:
        ax.plot(tx, ty, 'o', ms=6)
    if traj:
        xs = [p[0] for p in traj]; ys = [p[1] for p in traj]
        ax.plot(xs, ys, '-', lw=1)
    ax.set_aspect('equal'); ax.set_xlim(-1, 2*board.cols+1); ax.set_ylim(-1, 2*board.rows+1)
    ax.invert_yaxis(); ax.set_title('Lazor paths')
    plt.tight_layout(); plt.savefig(path, dpi=180); plt.close(fig)

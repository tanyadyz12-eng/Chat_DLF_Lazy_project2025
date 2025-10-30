
"""
render_plus.py
Richer visualization & report helpers.
"""
from __future__ import annotations
from typing import Dict, Tuple, List, Set
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

def save_text_with_header(path: str, board: Board, placements: Dict[Tuple[int,int], Block], hits:Set[Tuple[int,int]], elapsed: float, collision: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    solved = set(board.targets).issubset(hits)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Collision model : {collision}\n")
        f.write(f"Grid            : {board.rows} x {board.cols}\n")
        f.write(f"Stock           : A={board.stock.get('A',0)}, B={board.stock.get('B',0)}, C={board.stock.get('C',0)}\n")
        f.write(f"Lasers / Targets: {len(board.lasers)} / {len(board.targets)}\n")
        f.write(f"Solved          : {solved}\n")
        f.write(f"Targets hit     : {len(hits)} / {len(board.targets)}\n")
        f.write(f"Time            : {elapsed:.3f} s\n\n")
        if board.targets:
            missed = sorted(set(board.targets) - set(hits))
            if missed:
                f.write("Missed targets  : " + ', '.join(map(str, missed)) + "\n\n")
        f.write("Board (lowercase = movable block placed):\n")
        f.write(ascii_board(board, placements))
        f.write("\n")

def save_png_plus(path: str, board: Board, placements: Dict[Tuple[int,int], Block], traj: List[Tuple[int,int,int,int]], hits:Set[Tuple[int,int]], collision: str):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6,6))
    for r in range(board.rows):
        for c in range(board.cols):
            x0, y0 = 2*c, 2*r
            rect = plt.Rectangle((x0, y0), 2, 2, fill=False, linewidth=0.6, alpha=0.6)
            ax.add_patch(rect)
    for mapping, alpha in ((board.fixed, 0.45), (placements, 0.8)):
        for (r,c), blk in mapping.items():
            x0, y0 = 2*c, 2*r
            color = {'A':'#3b82f6','B':'#ef4444','C':'#10b981'}.get(blk.kind.value,'#999')
            rect = plt.Rectangle((x0, y0), 2, 2, color=color, alpha=alpha, lw=0.0)
            ax.add_patch(rect)
            ax.text(x0+1, y0+1, blk.kind.value if mapping is board.fixed else blk.kind.value.lower(),
                    ha='center', va='center', fontsize=10, color='white', weight='bold')
    for i, L in enumerate(board.lasers):
        ax.plot(L.x, L.y, marker='o', ms=6, linestyle='None', label='Laser' if i==0 else None)
    hits_set = set(hits)
    first_hit, first_miss = True, True
    for (tx,ty) in board.targets:
        if (tx,ty) in hits_set:
            ax.plot(tx, ty, marker='o', ms=7, color='#16a34a', linestyle='None',
                    label='Target (hit)' if first_hit else None)
            first_hit = False
        else:
            ax.plot(tx, ty, marker='x', ms=8, mew=2, color='#dc2626', linestyle='None',
                    label='Target (missed)' if first_miss else None)
            first_miss = False
    if traj:
        xs = [p[0] for p in traj]; ys = [p[1] for p in traj]
        ax.plot(xs, ys, '-', lw=1.2, color='#22c55e', label='Beam')
    ax.set_aspect('equal'); ax.set_xlim(-1, 2*board.cols+1); ax.set_ylim(-1, 2*board.rows+1)
    ax.invert_yaxis()
    ax.set_title(f"Lazor paths  •  {collision} collision", fontsize=12)
    ax.legend(loc='upper right', fontsize=9, frameon=True)
    import matplotlib.pyplot as plt
    plt.tight_layout(); plt.savefig(path, dpi=180); plt.close(fig)

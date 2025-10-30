
"""
model.py
Core data abstractions for Lazors.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, List, Optional, Set

class BlockType(Enum):
    REFLECT = 'A'
    OPAQUE  = 'B'
    REFRACT = 'C'

@dataclass(frozen=True)
class Block:
    kind: BlockType

@dataclass
class Laser:
    x: int
    y: int
    vx: int
    vy: int

@dataclass
class Board:
    grid: List[List[str]]
    stock: Dict[str, int]
    fixed: Dict[Tuple[int,int], Block]
    movable_slots: List[Tuple[int,int]]
    rows: int
    cols: int
    targets: Set[Tuple[int,int]]
    lasers: List[Laser]

    def in_bounds_cell(self, r:int, c:int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell_from_xy(self, x:int, y:int) -> Optional[Tuple[int,int]]:
        if x % 2 == 1 and y % 2 == 1:
            r = (y - 1) // 2
            c = (x - 1) // 2
            if self.in_bounds_cell(r, c):
                return (r, c)
        return None

    def get_block(self, r:int, c:int, placements:Dict[Tuple[int,int], Block]) -> Optional[Block]:
        if (r,c) in self.fixed:
            return self.fixed[(r,c)]
        return placements.get((r,c))

    def can_place(self, r:int, c:int) -> bool:
        return (r,c) in self.movable_slots and (r,c) not in self.fixed

def build_board(parsed: Dict) -> Board:
    grid = parsed['grid']
    rows, cols = parsed['shape']
    fixed = {}
    movable = []
    for r in range(rows):
        for c in range(cols):
            t = grid[r][c]
            if t in ('A','B','C'):
                bt = {'A':BlockType.REFLECT,'B':BlockType.OPAQUE,'C':BlockType.REFRACT}[t]
                fixed[(r,c)] = Block(bt)
            elif t == 'o':
                movable.append((r,c))
    lasers = [Laser(*L) for L in parsed['lasers']]
    targets = set(parsed['targets'])
    return Board(grid, parsed['stock'], fixed, movable, rows, cols, targets, lasers)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Course Submission · Highly Commented Version]
This file is part of the Lazor course project submission and has been
annotated with verbose, English-only comments to maximize readability.

• Role: Core data types (Board/Block/enums).
• Inputs: —
• Outputs: Data classes/enums for other modules
• Design notes:
  1) Interfaces are consistent with `model.py` / `bff_parser.py` / `simulate(_wall).py` / `render_plus.py`;
  2) All reproducible behaviors (CLI, JSON schema, artifact naming) match the README;
  3) Key functions include type hints and docstrings for TA-friendly review.

Coordinate convention: grid intersections are integers; block centers are odd coordinates (half-step model),
which matches the BFF specification used in class.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple, List, Set


class BlockType(Enum):
    """Block type enumeration.
    
    Attributes:
        REFLECT: Reflect block (A), reflects laser when hit
        OPAQUE: Opaque block (B), stops laser when hit
        REFRACT: Refract block (C), creates multiple rays when hit
    """
    REFLECT = 'A'
    OPAQUE  = 'B'
    REFRACT = 'C'


@dataclass(frozen=True)
class Block:
    """Block class.
    
    Represents a block in the game, which can be reflect, opaque, or refract type.
    
    Attributes:
        kind: Block type (BlockType enumeration)
    """
    kind: BlockType


@dataclass(frozen=True)
class Laser:
    """Laser class.
    
    Represents a laser beam in the game, containing position and direction information.
    
    Attributes:
        x: Laser starting X coordinate
        y: Laser starting Y coordinate
        vx: X direction velocity component (-1, 0, or 1)
        vy: Y direction velocity component (-1, 0, or 1)
    """
    x: int
    y: int
    vx: int
    vy: int


@dataclass
class Board:
    """Game board class.
    
    Represents the entire Lazor game board, containing grid, blocks, lasers, and targets.
    
    Attributes:
        rows: Number of rows in the board
        cols: Number of columns in the board
        grid: Grid representation (2D list)
        fixed: Dictionary of fixed blocks, key is (row, col), value is Block object
        movable_slots: List of positions where blocks can be placed
        targets: Set of target points, each target is (x, y) tuple
        lasers: List of lasers
        stock: Dictionary of available block inventory, key is 'A'/'B'/'C', value is count
    """
    rows: int
    cols: int
    grid: List[List[str]]
    fixed: Dict[Tuple[int, int], Block]
    movable_slots: List[Tuple[int, int]]
    targets: Set[Tuple[int, int]]
    lasers: List[Laser]
    stock: Dict[str, int] = field(default_factory=dict)
    
    def center_of(self, r: int, c: int) -> Tuple[int, int]:
        """Calculate the center coordinates of a block.
        
        Args:
            r: Row index
            c: Column index
            
        Returns:
            (x, y) center coordinate tuple
        """
        return (2*c+1, 2*r+1)
    
    def in_bounds_center(self, x: int, y: int) -> bool:
        """Check if coordinates are within board boundaries.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if coordinates are within bounds, False otherwise
        """
        return -1 <= x <= 2*self.cols+1 and -1 <= y <= 2*self.rows+1

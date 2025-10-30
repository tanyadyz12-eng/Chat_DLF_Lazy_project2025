
"""
simulate.py
Center-collision: interact at cell centers (x,y both odd).
"""
from __future__ import annotations
from typing import Dict, Tuple, List, Set
from model import Board, BlockType, Block, Laser

MAX_STEPS_FACTOR = 8

def reflect_direction(vx:int, vy:int, prefer_axis:str='auto') -> Tuple[int,int]:
    if prefer_axis == 'x':
        return (-vx, vy)
    if prefer_axis == 'y':
        return (vx, -vy)
    return (-vx, -vy)

def apply_interaction(block: BlockType, beam: Laser, last_axis: str='auto') -> List[Laser]:
    if block == BlockType.OPAQUE:
        return []
    if block == BlockType.REFLECT:
        nvx, nvy = reflect_direction(beam.vx, beam.vy, last_axis)
        return [Laser(beam.x, beam.y, nvx, nvy)]
    if block == BlockType.REFRACT:
        cont = Laser(beam.x, beam.y, beam.vx, beam.vy)
        nvx, nvy = reflect_direction(beam.vx, beam.vy, last_axis)
        refl = Laser(beam.x, beam.y, nvx, nvy)
        return [cont, refl]
    return []

def trace(board: Board, placements: Dict[Tuple[int,int], Block], max_steps:int=None):
    visited: Set[Tuple[int,int,int,int]] = set()
    hit = set()
    traj: List[Tuple[int,int,int,int]] = []

    beams: List[Laser] = [Laser(L.x, L.y, L.vx, L.vy) for L in board.lasers]
    step_bound = max_steps or MAX_STEPS_FACTOR * (board.rows + board.cols) * 10

    while beams:
        beam = beams.pop()
        steps = 0
        while steps < step_bound:
            nx, ny = beam.x + beam.vx, beam.y + beam.vy
            state = (nx, ny, beam.vx, beam.vy)
            traj.append((nx, ny, beam.vx, beam.vy))
            if state in visited:
                break
            visited.add(state)

            if (nx, ny) in board.targets:
                hit.add((nx, ny))

            if nx % 2 == 1 and ny % 2 == 1:
                r = (ny - 1) // 2
                c = (nx - 1) // 2
                if 0 <= r < board.rows and 0 <= c < board.cols:
                    blk = board.get_block(r, c, placements)
                    if blk:
                        axis = 'x' if beam.vy == 0 else 'y'
                        new_beams = apply_interaction(blk.kind, Laser(nx, ny, beam.vx, beam.vy), last_axis=axis)
                        if not new_beams:
                            break
                        beams.extend(new_beams)
                        break

            beam.x, beam.y = nx, ny
            steps += 1
    return hit, traj

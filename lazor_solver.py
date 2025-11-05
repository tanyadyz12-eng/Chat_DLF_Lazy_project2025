"""
Lazor Board Game Solver

This module solves Lazor board game puzzles by:
1. Reading board configuration from .bff files
2. Placing blocks in valid positions
3. Simulating laser paths
4. Finding solutions where lasers hit all target points

"""

import itertools
from typing import List, Tuple, Set, Dict, Optional
from copy import deepcopy
import time


class Block:
    """
    Represents a block in the Lazor game.

    Attributes:
        block_type (str): Type of block - 'A' (reflect), 'B' (opaque), 'C' (refract)
        position (tuple): Position (x, y) on the grid
        is_fixed (bool): Whether the block is fixed in position
    """

    # Block type constants
    REFLECT = 'A'
    OPAQUE = 'B'
    REFRACT = 'C'

    def __init__(self, block_type: str, position: Tuple[int, int] = None,
                 is_fixed: bool = False):
        """
        Initialize a Block.

        Args:
            block_type: Type of block ('A', 'B', or 'C')
            position: Position (x, y) on grid
            is_fixed: Whether block is fixed in position
        """
        if block_type not in [self.REFLECT, self.OPAQUE, self.REFRACT]:
            raise ValueError(f"Invalid block type: {block_type}")

        self.block_type = block_type
        self.position = position
        self.is_fixed = is_fixed

    def interact_with_laser(self, edge: str, laser_dir: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Calculate new laser direction(s) after interaction with this block.

        Args:
            edge: Which edge was hit ('left', 'right', 'top', 'bottom')
            laser_dir: Current laser direction (vx, vy)

        Returns:
            List of new direction tuples
        """
        vx, vy = laser_dir

        if self.block_type == self.OPAQUE:
            # Opaque blocks stop the laser
            return []

        elif self.block_type == self.REFLECT:
            # Reflect blocks bounce the laser
            if edge in ['left', 'right']:
                # Hit vertical edge, reverse x direction
                return [(-vx, vy)]
            else:  # top or bottom
                # Hit horizontal edge, reverse y direction
                return [(vx, -vy)]

        elif self.block_type == self.REFRACT:
            # Refract blocks let laser pass through AND create a reflection
            results = []

            # Continue in same direction
            results.append((vx, vy))

            # Also create a reflection
            if edge in ['left', 'right']:
                results.append((-vx, vy))
            else:  # top or bottom
                results.append((vx, -vy))

            return results

    def __repr__(self):
        """String representation of the block."""
        return f"Block({self.block_type}, {self.position}, fixed={self.is_fixed})"


class Laser:
    """
    Represents a laser beam in the game.

    Attributes:
        start_pos (tuple): Starting position (x, y)
        direction (tuple): Direction vector (vx, vy)
    """

    def __init__(self, start_pos: Tuple[int, int], direction: Tuple[int, int]):
        """
        Initialize a Laser.

        Args:
            start_pos: Starting position (x, y)
            direction: Direction vector (vx, vy)
        """
        self.start_pos = start_pos
        self.direction = direction

    def __repr__(self):
        """String representation of the laser."""
        return f"Laser({self.start_pos}, {self.direction})"


class Board:
    """
    Represents the Lazor game board.

    Attributes:
        grid (list): 2D grid layout
        width (int): Grid width
        height (int): Grid height
        blocks (dict): Dictionary mapping positions to Block objects
        lasers (list): List of Laser objects
        target_points (set): Set of points that must be hit
        available_blocks (dict): Count of available blocks by type
    """

    def __init__(self, grid: List[List[str]]):
        """
        Initialize a Board.

        Args:
            grid: 2D grid layout with 'o', 'x', 'A', 'B', 'C'
        """
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.blocks = {}
        self.lasers = []
        self.target_points = set()
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}

        # Extract fixed blocks from grid
        self._extract_fixed_blocks()

    def _extract_fixed_blocks(self):
        """Extract fixed blocks from the grid."""
        for row_idx, row in enumerate(self.grid):
            for col_idx, cell in enumerate(row):
                if cell in ['A', 'B', 'C']:
                    # Convert grid position to board coordinates
                    # Grid position (col, row) -> Board position (col*2+1, row*2+1)
                    pos = (col_idx * 2 + 1, row_idx * 2 + 1)
                    self.blocks[pos] = Block(cell, pos, is_fixed=True)

    def get_valid_positions(self) -> List[Tuple[int, int]]:
        """
        Get all valid positions where blocks can be placed.

        Returns:
            List of valid (x, y) positions
        """
        valid_positions = []
        for row_idx, row in enumerate(self.grid):
            for col_idx, cell in enumerate(row):
                if cell == 'o':
                    # Convert to board coordinates
                    pos = (col_idx * 2 + 1, row_idx * 2 + 1)
                    if pos not in self.blocks:  # Not already occupied by fixed block
                        valid_positions.append(pos)
        return valid_positions

    def place_block(self, block_type: str, position: Tuple[int, int]):
        """
        Place a block at the specified position.

        Args:
            block_type: Type of block ('A', 'B', or 'C')
            position: Position (x, y) to place block
        """
        self.blocks[position] = Block(block_type, position, is_fixed=False)

    def remove_block(self, position: Tuple[int, int]):
        """
        Remove a block from the specified position.

        Args:
            position: Position (x, y) to remove block from
        """
        if position in self.blocks and not self.blocks[position].is_fixed:
            del self.blocks[position]

    def get_block_at_edge(self, x: int, y: int) -> Optional[Tuple[Block, str]]:
        """
        Get the block at a specific edge position and which edge was hit.

        Args:
            x: X-coordinate
            y: Y-coordinate

        Returns:
            Tuple of (Block, edge) or None, where edge is 'left', 'right', 'top', or 'bottom'
        """
        # Check all blocks to see if this position is on their edge
        # A block at position (bx, by) occupies the space from (bx-1, by-1) to (bx+1, by+1)
        # The edges are at bx-1, bx+1 (vertical) and by-1, by+1 (horizontal)
        for pos, block in self.blocks.items():
            block_x, block_y = pos

            # Check if on left vertical edge (x = block_x - 1)
            if x == block_x - 1 and block_y - 1 <= y <= block_y + 1:
                return (block, 'left')

            # Check if on right vertical edge (x = block_x + 1)
            if x == block_x + 1 and block_y - 1 <= y <= block_y + 1:
                return (block, 'right')

            # Check if on top horizontal edge (y = block_y - 1)
            if y == block_y - 1 and block_x - 1 <= x <= block_x + 1:
                return (block, 'top')

            # Check if on bottom horizontal edge (y = block_y + 1)
            if y == block_y + 1 and block_x - 1 <= x <= block_x + 1:
                return (block, 'bottom')

        return None

    def simulate_lasers(self) -> Set[Tuple[int, int]]:
        """
        Simulate all lasers and return all points they pass through.

        Returns:
            Set of (x, y) points that lasers passed through
        """
        hit_points = set()

        for laser in self.lasers:
            # Track laser paths using queue to handle multiple beams (from refraction)
            beams = [(laser.start_pos, laser.direction)]
            visited = set()

            while beams:
                pos, direction = beams.pop(0)
                x, y = pos
                vx, vy = direction

                # Avoid infinite loops
                state = (x, y, vx, vy)
                if state in visited:
                    continue
                visited.add(state)

                # Check bounds (assuming max size based on grid)
                max_x = self.width * 2 + 2
                max_y = self.height * 2 + 2

                if x < 0 or x > max_x or y < 0 or y > max_y:
                    continue

                # Limit iterations to prevent infinite loops
                if len(visited) > 1000:
                    break

                # Record this point
                hit_points.add((x, y))

                # Calculate next position
                next_x = x + vx
                next_y = y + vy

                # Check if next position is on a block edge
                block_info = self.get_block_at_edge(next_x, next_y)

                if block_info:
                    block, edge = block_info
                    # Interact with the block
                    new_directions = block.interact_with_laser(edge, (vx, vy))

                    for new_dir in new_directions:
                        beams.append(((next_x, next_y), new_dir))
                else:
                    # Continue in the same direction
                    beams.append(((next_x, next_y), (vx, vy)))

        return hit_points

    def check_solution(self) -> bool:
        """
        Check if the current board configuration solves the puzzle.

        Returns:
            True if all target points are hit, False otherwise
        """
        hit_points = self.simulate_lasers()
        return self.target_points.issubset(hit_points)

    def __repr__(self):
        """String representation of the board."""
        return f"Board({self.width}x{self.height}, {len(self.blocks)} blocks, {len(self.lasers)} lasers)"


class BFFParser:
    """
    Parser for .bff (Board File Format) files.
    """

    @staticmethod
    def parse_file(filename: str) -> Board:
        """
        Parse a .bff file and create a Board object.

        Args:
            filename: Path to .bff file

        Returns:
            Board object with all configuration loaded

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Parse grid
        grid = []
        in_grid = False
        lasers = []
        target_points = set()
        available_blocks = {'A': 0, 'B': 0, 'C': 0}

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            if line == 'GRID START':
                in_grid = True
                continue
            elif line == 'GRID STOP':
                in_grid = False
                continue

            if in_grid:
                # Parse grid row
                row = line.split()
                grid.append(row)
            else:
                # Parse other elements
                parts = line.split()
                if not parts:
                    continue

                cmd = parts[0]

                if cmd in ['A', 'B', 'C']:
                    # Available blocks
                    available_blocks[cmd] = int(parts[1])
                elif cmd == 'L':
                    # Laser: L x y vx vy
                    x, y, vx, vy = map(int, parts[1:5])
                    lasers.append(Laser((x, y), (vx, vy)))
                elif cmd == 'P':
                    # Target point: P x y
                    x, y = map(int, parts[1:3])
                    target_points.add((x, y))

        # Create board
        board = Board(grid)
        board.lasers = lasers
        board.target_points = target_points
        board.available_blocks = available_blocks

        return board


class LazorSolver:
    """
    Solver for Lazor board game puzzles.
    """

    def __init__(self, board: Board):
        """
        Initialize the solver.

        Args:
            board: Board object to solve
        """
        self.board = board
        self.solution = None

    def solve(self) -> Optional[Dict[Tuple[int, int], str]]:
        """
        Solve the puzzle and return the solution.

        Returns:
            Dictionary mapping positions to block types, or None if no solution
        """
        # Get valid positions for placing blocks
        valid_positions = self.board.get_valid_positions()

        # Create list of blocks to place
        blocks_to_place = []
        for block_type, count in self.board.available_blocks.items():
            blocks_to_place.extend([block_type] * count)

        if not blocks_to_place:
            # No blocks to place, just check if current configuration works
            if self.board.check_solution():
                return {}
            else:
                return None

        # Optimization: limit positions to place blocks
        # We only need to check combinations, not permutations
        num_blocks = len(blocks_to_place)

        if num_blocks > len(valid_positions):
            return None  # More blocks than positions

        # Try all combinations of positions
        for position_combo in itertools.combinations(valid_positions, num_blocks):
            # Try all permutations of blocks for these positions
            for block_perm in itertools.permutations(blocks_to_place):
                # Place blocks
                placement = {}
                for pos, block_type in zip(position_combo, block_perm):
                    self.board.place_block(block_type, pos)
                    placement[pos] = block_type

                # Check if this solves the puzzle
                if self.board.check_solution():
                    self.solution = placement
                    return placement

                # Remove blocks for next iteration
                for pos in position_combo:
                    self.board.remove_block(pos)

        return None

    def solve_optimized(self) -> Optional[Dict[Tuple[int, int], str]]:
        """
        Optimized solver using smarter search strategy.

        First tries with all blocks (fast path), then tries subsets if needed.
        This handles both cases efficiently.

        Returns:
            Dictionary mapping positions to block types, or None if no solution
        """
        valid_positions = self.board.get_valid_positions()
        blocks_to_place = []

        for block_type, count in self.board.available_blocks.items():
            blocks_to_place.extend([block_type] * count)

        if not blocks_to_place:
            if self.board.check_solution():
                return {}
            else:
                return None

        num_blocks = len(blocks_to_place)

        if num_blocks > len(valid_positions):
            return None  # More blocks than positions

        from collections import Counter

        # FAST PATH: First try with all blocks (most common case)
        block_counter = Counter(blocks_to_place)
        result = self._solve_with_combinations(valid_positions, block_counter)
        if result is not None:
            return result

        # SLOW PATH: Try with fewer blocks, starting from largest subsets
        # Only try meaningful subsets (not all possible combinations)
        for num_to_place in range(num_blocks - 1, 0, -1):
            # Generate unique subsets by trying different counts of each block type
            seen_counters = set()

            for block_subset in itertools.combinations(blocks_to_place, num_to_place):
                counter = Counter(block_subset)
                counter_key = tuple(sorted(counter.items()))

                if counter_key in seen_counters:
                    continue
                seen_counters.add(counter_key)

                result = self._solve_with_combinations(valid_positions, counter)
                if result is not None:
                    return result

        # Try with no blocks
        if self.board.check_solution():
            return {}

        return None

    def _solve_with_combinations(self, valid_positions: List[Tuple[int, int]],
                                 block_counter: Dict[str, int]) -> Optional[Dict[Tuple[int, int], str]]:
        """
        Solve using combinations, avoiding redundant permutations.

        Args:
            valid_positions: List of valid positions
            block_counter: Counter of blocks by type

        Returns:
            Solution dictionary or None
        """
        total_blocks = sum(block_counter.values())

        # Generate all position combinations
        for position_combo in itertools.combinations(valid_positions, total_blocks):
            # Generate all ways to assign blocks to these positions
            # We need to generate all unique assignments
            for assignment in self._generate_assignments(list(position_combo), block_counter):
                # Place blocks
                placement = {}
                for pos, block_type in assignment.items():
                    self.board.place_block(block_type, pos)
                    placement[pos] = block_type

                # Check if this solves the puzzle
                if self.board.check_solution():
                    self.solution = placement
                    return placement

                # Remove blocks for next iteration
                for pos in assignment.keys():
                    self.board.remove_block(pos)

        return None

    def _generate_assignments(self, positions: List[Tuple[int, int]],
                             block_counter: Dict[str, int]) -> List[Dict[Tuple[int, int], str]]:
        """
        Generate all unique ways to assign blocks to positions.

        Args:
            positions: List of positions
            block_counter: Counter of blocks by type

        Returns:
            List of assignment dictionaries
        """
        if not positions or not block_counter:
            return [{}]

        if sum(block_counter.values()) == 0:
            return [{}]

        results = []

        # Try assigning each block type to the first position
        for block_type, count in block_counter.items():
            if count == 0:
                continue

            # Assign this block type to the first position
            new_counter = block_counter.copy()
            new_counter[block_type] -= 1
            if new_counter[block_type] == 0:
                del new_counter[block_type]

            # Recursively assign remaining blocks
            for sub_assignment in self._generate_assignments(positions[1:], new_counter):
                assignment = {positions[0]: block_type}
                assignment.update(sub_assignment)
                results.append(assignment)

        return results


class SolutionWriter:
    """
    Writes solutions to output files.
    """

    @staticmethod
    def write_text_solution(filename: str, board: Board,
                           solution: Dict[Tuple[int, int], str]):
        """
        Write solution to a text file.

        Args:
            filename: Output filename
            board: Board object
            solution: Solution dictionary
        """
        with open(filename, 'w') as f:
            f.write("LAZOR BOARD SOLUTION\n")
            f.write("=" * 50 + "\n\n")

            # Write grid with solution
            f.write("Board Configuration:\n")
            for row_idx in range(board.height):
                row_str = ""
                for col_idx in range(board.width):
                    pos = (col_idx * 2 + 1, row_idx * 2 + 1)

                    if pos in board.blocks:
                        block = board.blocks[pos]
                        if block.is_fixed:
                            row_str += f"[{block.block_type}] "
                        else:
                            row_str += f" {block.block_type}  "
                    elif board.grid[row_idx][col_idx] == 'o':
                        row_str += " o  "
                    else:
                        row_str += " x  "

                f.write(row_str + "\n")

            f.write("\n" + "=" * 50 + "\n")
            f.write("Block Placement:\n")
            for pos, block_type in sorted(solution.items()):
                grid_x = (pos[0] - 1) // 2
                grid_y = (pos[1] - 1) // 2
                f.write(f"  Block {block_type} at grid position ({grid_x}, {grid_y})\n")

            f.write("\n" + "=" * 50 + "\n")
            f.write("Target Points Hit:\n")
            hit_points = board.simulate_lasers()
            for point in sorted(board.target_points):
                status = "[+]" if point in hit_points else "[-]"
                f.write(f"  {status} Point {point}\n")

            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Solution Status: {'SOLVED' if board.check_solution() else 'NOT SOLVED'}\n")


def solve_lazor_file(input_file: str, output_file: str = None) -> bool:
    """
    Solve a Lazor puzzle from a .bff file.

    Args:
        input_file: Path to input .bff file
        output_file: Path to output solution file (optional)

    Returns:
        True if solved, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Solving: {input_file}")
    print(f"{'='*60}")

    start_time = time.time()

    # Parse the file
    try:
        board = BFFParser.parse_file(input_file)
        print(f"Board size: {board.width}x{board.height}")
        print(f"Available blocks: {board.available_blocks}")
        print(f"Lasers: {len(board.lasers)}")
        print(f"Target points: {len(board.target_points)}")
    except Exception as e:
        print(f"Error parsing file: {e}")
        return False

    # Solve the puzzle
    print("\nSolving...")
    solver = LazorSolver(board)

    # Use optimized solver for better performance
    solution = solver.solve_optimized()

    elapsed_time = time.time() - start_time

    if solution is not None:
        print(f"\n[+] SOLUTION FOUND in {elapsed_time:.2f} seconds!")
        print(f"Blocks placed: {len(solution)}")

        # Write solution to file
        if output_file is None:
            output_file = input_file.replace('.bff', '_solution.txt')

        SolutionWriter.write_text_solution(output_file, board, solution)
        print(f"Solution written to: {output_file}")

        return True
    else:
        print(f"\n[-] NO SOLUTION FOUND (searched for {elapsed_time:.2f} seconds)")
        return False


if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) > 1:
        # Solve specific file from command line
        input_file = sys.argv[1]
        solve_lazor_file(input_file)
    else:
        # Solve all .bff files in current directory
        bff_files = [f for f in os.listdir('.') if f.endswith('.bff')]

        if not bff_files:
            print("No .bff files found in current directory")
            print("\nUsage: python lazor_solver.py [filename.bff]")
        else:
            print(f"Found {len(bff_files)} .bff files")

            results = []
            for bff_file in sorted(bff_files):
                solved = solve_lazor_file(bff_file)
                results.append((bff_file, solved))

            # Summary
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            for filename, solved in results:
                status = "[+] SOLVED" if solved else "[-] FAILED"
                print(f"{status}: {filename}")

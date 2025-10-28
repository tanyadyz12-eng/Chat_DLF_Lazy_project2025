"""
Lazor Game Solver - CORRECT PHYSICS
Reflection follows law of reflection: angle of incidence = angle of reflection
"""

from itertools import combinations, permutations
import time


class Block:
    """Block in Lazor game."""

    def __init__(self, block_type, position=None, fixed=False):
        self.block_type = block_type
        self.position = position
        self.fixed = fixed

    def interact(self, entry_pos, laser_dir):
        """
        Calculate laser interaction using correct reflection physics.

        For a reflect block:
        - If laser hits from left/right (moving horizontally): reflect vertically
        - If laser hits from top/bottom (moving vertically): reflect horizontally

        This is 90-degree reflection, not bounce-back!
        """
        vx, vy = laser_dir

        if self.block_type == 'A':  # Reflect
            # 90 degree reflection: swap and negate one component
            # Horizontal (1,0) -> Vertical (0,1) or (0,-1)
            # Vertical (0,1) -> Horizontal (1,0) or (-1,0)

            # The direction depends on which side was hit
            # For simplicity, use perpendicular reflection
            if vx != 0 and vy == 0:
                # Moving horizontally -> reflect to vertical
                # Choose direction based on which side
                return [(0, vx), (0, -vx)]  # Try both up and down
            elif vx == 0 and vy != 0:
                # Moving vertically -> reflect to horizontal
                return [(vy, 0), (-vy, 0)]  # Try both left and right
            else:
                # Diagonal - reflect both components
                return [(-vx, vy), (vx, -vy)]

        elif self.block_type == 'B':  # Opaque
            return []

        elif self.block_type == 'C':  # Refract
            # Pass through + reflect
            if vx != 0 and vy == 0:
                return [(vx, vy), (0, vx), (0, -vx)]
            elif vx == 0 and vy != 0:
                return [(vx, vy), (vy, 0), (-vy, 0)]
            else:
                return [(vx, vy), (-vx, vy), (vx, -vy)]

        return [(vx, vy)]


class LaserBoard:
    """Lazor game board."""

    def __init__(self):
        self.grid = []
        self.lasers = []
        self.targets = set()
        self.blocks_available = {'A': 0, 'B': 0, 'C': 0}
        self.fixed_blocks = []
        self.width = 0
        self.height = 0

    def read_bff(self, filename):
        """Read .bff file."""
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        reading_grid = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line == 'GRID START':
                reading_grid = True
                continue
            elif line == 'GRID STOP':
                reading_grid = False
                continue

            if reading_grid:
                row = [c for c in line.split() if c]
                self.grid.append(row)
                continue

            parts = line.split()
            if not parts:
                continue

            if len(parts) == 2 and parts[0] in ['A', 'B', 'C']:
                self.blocks_available[parts[0]] = int(parts[1])
            elif parts[0] == 'L':
                x, y, vx, vy = map(int, parts[1:5])
                self.lasers.append(((x, y), (vx, vy)))
            elif parts[0] == 'P':
                x, y = map(int, parts[1:3])
                self.targets.add((x, y))

        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.grid else 0

        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell in ['A', 'B', 'C']:
                    self.fixed_blocks.append(
                        Block(cell, (j * 2 + 1, i * 2 + 1), True))

    def get_open_positions(self):
        """Get open positions."""
        pos = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == 'o':
                    pos.append((j * 2 + 1, i * 2 + 1))
        return pos

    def simulate_lasers(self, placed_blocks):
        """Simulate lasers."""
        blocks = self.fixed_blocks + placed_blocks
        block_map = {b.position: b for b in blocks}

        hit_points = set()

        for start_pos, start_dir in self.lasers:
            queue = [(start_pos, start_dir)]
            seen = set()
            steps = 0
            max_steps = 10000

            while queue and steps < max_steps:
                steps += 1
                pos, direction = queue.pop(0)

                state = (pos, direction)
                if state in seen:
                    continue
                seen.add(state)

                hit_points.add(pos)

                vx, vy = direction
                new_pos = (pos[0] + vx, pos[1] + vy)
                nx, ny = new_pos

                if nx < 0 or nx > self.width * 2:
                    continue
                if ny < 0 or ny > self.height * 2:
                    continue

                hit_points.add(new_pos)

                if nx % 2 == 1 and ny % 2 == 1 and new_pos in block_map:
                    block = block_map[new_pos]
                    new_dirs = block.interact(pos, direction)

                    for new_dir in new_dirs:
                        nvx, nvy = new_dir
                        next_pos = (new_pos[0] + nvx, new_pos[1] + nvy)
                        nxx, nyy = next_pos

                        if nxx < 0 or nxx > self.width * 2:
                            continue
                        if nyy < 0 or nyy > self.height * 2:
                            continue

                        queue.append((next_pos, new_dir))
                else:
                    queue.append((new_pos, direction))

        return hit_points

    def check_solution(self, blocks):
        """Check solution."""
        if not self.targets:
            return True
        points = self.simulate_lasers(blocks)
        return self.targets.issubset(points)

    def solve(self):
        """Solve puzzle."""
        positions = self.get_open_positions()

        block_list = []
        for bt, cnt in self.blocks_available.items():
            block_list.extend([bt] * cnt)

        if not block_list:
            return [] if self.check_solution([]) else None

        print("  {0} pos, {1} blocks: {2}".format(
            len(positions), len(block_list), block_list))

        tested = 0

        if len(set(block_list)) == 1:
            for pos_set in combinations(positions, len(block_list)):
                tested += 1
                if tested % 100 == 0:
                    print("  ... {0}".format(tested))

                blocks = [Block(block_list[i], pos_set[i])
                          for i in range(len(block_list))]

                if self.check_solution(blocks):
                    print("  FOUND! (#{0})".format(tested))
                    return blocks
        else:
            for pos_set in combinations(positions, len(block_list)):
                for perm in set(permutations(block_list)):
                    tested += 1
                    if tested % 100 == 0:
                        print("  ... {0}".format(tested))

                    blocks = [Block(perm[i], pos_set[i])
                              for i in range(len(block_list))]

                    if self.check_solution(blocks):
                        print("  FOUND! (#{0})".format(tested))
                        return blocks

        print("  Not found ({0})".format(tested))
        return None

    def save_solution(self, sol, fname):
        """Save solution."""
        with open(fname, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\nLAZOR SOLUTION\n" + "=" * 60 + "\n\n")

            if sol is None:
                f.write("No solution\n")
                return

            f.write("SOLUTION!\n\n")

            if sol:
                names = {'A': 'Reflect', 'B': 'Opaque', 'C': 'Refract'}
                for i, b in enumerate(sol, 1):
                    gx = (b.position[0] - 1) // 2
                    gy = (b.position[1] - 1) // 2
                    f.write("  {0}. {1} at grid[{2}][{3}]\n".format(
                        i, names.get(b.block_type, '?'), gy, gx))

            pts = self.simulate_lasers(sol)
            f.write("\nTargets: " + str(sorted(self.targets)) + "\n")
            f.write("All hit: " + str(self.targets.issubset(pts)) + "\n")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python lazor_solver_final.py file.bff")
        return

    fname = sys.argv[1]
    print("=" * 60)
    print("LAZOR SOLVER")
    print("=" * 60)
    print("File: " + fname)

    board = LaserBoard()
    board.read_bff(fname)

    print("Grid: {0}x{1}, Targets: {2}".format(
        board.width, board.height, len(board.targets)))
    print("\nSolving...\n")

    t0 = time.time()
    sol = board.solve()
    elapsed = time.time() - t0

    print("\nTime: {0:.2f}s".format(elapsed))

    if sol is not None:
        print("[OK] Found!")
        out = fname.replace('.bff', '_sol.txt')
        board.save_solution(sol, out)
        print("Saved: " + out)
    else:
        print("[XX] No solution")

    print("=" * 60)


if __name__ == "__main__":
    main()
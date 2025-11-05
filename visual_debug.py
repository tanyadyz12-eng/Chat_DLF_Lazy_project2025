"""Visual debug script for Lazor solver"""

from lazor_solver import BFFParser

def visualize_laser_path(board):
    """Create a visual representation of the board and laser paths"""
    max_x = board.width * 2 + 3
    max_y = board.height * 2 + 3

    # Create a grid for visualization
    grid = [['.' for _ in range(max_x)] for _ in range(max_y)]

    # Mark blocks
    for pos, block in board.blocks.items():
        bx, by = pos
        # Mark block center
        grid[by][bx] = block.block_type

        # Mark block edges
        if bx > 0:
            grid[by][bx - 1] = '#'
        if bx + 1 < max_x:
            grid[by][bx + 1] = '#'
        if by > 0:
            grid[by - 1][bx] = '#'
        if by + 1 < max_y:
            grid[by + 1][bx] = '#'

    # Simulate lasers and mark hit points
    hit_points = board.simulate_lasers()

    for x, y in hit_points:
        if 0 <= y < max_y and 0 <= x < max_x:
            if grid[y][x] == '.':
                grid[y][x] = '*'

    # Mark laser starting points
    for laser in board.lasers:
        x, y = laser.start_pos
        if 0 <= y < max_y and 0 <= x < max_x:
            grid[y][x] = 'L'

    # Mark target points
    for x, y in board.target_points:
        if 0 <= y < max_y and 0 <= x < max_x:
            if (x, y) in hit_points:
                grid[y][x] = 'T'  # Hit target
            else:
                grid[y][x] = 't'  # Missed target

    # Print the grid
    print("\nBoard Visualization:")
    print("  " + "".join(str(i % 10) for i in range(max_x)))
    for idx, row in enumerate(grid):
        print(f"{idx} " + "".join(row))

    print("\nLegend:")
    print("  L = Laser start")
    print("  * = Laser path")
    print("  T = Target hit")
    print("  t = Target missed")
    print("  A/B/C = Block (A=reflect, B=opaque, C=refract)")
    print("  # = Block edge")
    print("  . = Empty space")

    print(f"\nHit points: {len(hit_points)}")
    print(f"Targets: {len(board.target_points)}")
    print(f"Targets hit: {len(board.target_points.intersection(hit_points))}")
    print(f"Solution: {board.check_solution()}")


# Test with tiny_5.bff
print("="*60)
print("Testing tiny_5.bff")
print("="*60)

board = BFFParser.parse_file('tiny_5.bff')
print(f"Grid: {board.width}x{board.height}")
print(f"Blocks to place: {board.available_blocks}")
print(f"Fixed blocks: {[(pos, b.block_type) for pos, b in board.blocks.items() if b.is_fixed]}")
print(f"Lasers: {board.lasers}")
print(f"Targets: {board.target_points}")

visualize_laser_path(board)

# Try a specific configuration
print("\n" + "="*60)
print("Testing with A blocks at (1,3), (3,5), (5,3) and C at (5,5)")
print("="*60)

board.place_block('A', (1, 3))
board.place_block('A', (3, 5))
board.place_block('A', (5, 3))
board.place_block('C', (5, 5))

visualize_laser_path(board)

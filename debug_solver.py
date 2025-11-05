"""Debug script for Lazor solver"""

from lazor_solver import BFFParser, LazorSolver

def visualize_board(board, hit_points=None):
    """Visualize the board and laser paths"""
    max_x = board.width * 2 + 2
    max_y = board.height * 2 + 2

    print(f"\nBoard visualization (max_x={max_x}, max_y={max_y}):")
    print(f"Grid size: {board.width}x{board.height}")
    print(f"Blocks: {board.blocks}")
    print(f"Lasers: {board.lasers}")
    print(f"Target points: {board.target_points}")

    if hit_points:
        print(f"\nHit points: {sorted(hit_points)}")
        print(f"Target points hit: {board.target_points.intersection(hit_points)}")
        print(f"Target points missed: {board.target_points - hit_points}")

# Test with tiny_5.bff
board = BFFParser.parse_file('tiny_5.bff')
visualize_board(board)

# Simulate without any movable blocks
hit_points = board.simulate_lasers()
visualize_board(board, hit_points)

# Try placing one A block at different positions
print("\n" + "="*60)
print("Testing block placements:")
print("="*60)

valid_positions = board.get_valid_positions()
print(f"Valid positions: {valid_positions}")

for pos in valid_positions[:3]:  # Test first 3 positions
    board.place_block('A', pos)
    hit_points = board.simulate_lasers()
    print(f"\nBlock A at {pos}:")
    print(f"  Targets hit: {board.target_points.intersection(hit_points)}")
    print(f"  Solution: {board.check_solution()}")
    board.remove_block(pos)

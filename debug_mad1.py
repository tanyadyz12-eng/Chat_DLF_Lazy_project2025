"""Detailed debug of mad_1"""

from lazor_solver import BFFParser
from visual_debug import visualize_laser_path

board = BFFParser.parse_file('mad_1.bff')
print("MAD_1 Board Analysis")
print("="*60)
print(f"Grid: {board.width}x{board.height}")
print(f"Blocks to place: {board.available_blocks}")  # A=2, C=1
print(f"Lasers: {board.lasers}")  # L 2 7 1 -1
print(f"Targets: {sorted(board.target_points)}")  # P 3 0, P 4 3, P 2 5, P 4 7

# Show initial state
visualize_laser_path(board)

# The laser starts at (2, 7) going (1, -1) which is right and up
# Without blocks, it should go: (2,7) -> (3,6) -> (4,5) -> (5,4) -> (6,3) -> (7,2) -> (8,1) -> (9,0)

# Let's try placing some blocks
print("\n" + "="*60)
print("Test 1: Place A at (3, 1)")
print("="*60)

board2 = BFFParser.parse_file('mad_1.bff')
board2.place_block('A', (3, 1))
visualize_laser_path(board2)

print("\n" + "="*60)
print("Test 2: Place A at (5, 5)")
print("="*60)

board3 = BFFParser.parse_file('mad_1.bff')
board3.place_block('A', (5, 5))
visualize_laser_path(board3)

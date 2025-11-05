"""Debug showstopper_4"""

from lazor_solver import BFFParser
from visual_debug import visualize_laser_path

board = BFFParser.parse_file('showstopper_4.bff')
print(f"Grid: {board.width}x{board.height}")
print(f"Blocks to place: {board.available_blocks}")
print(f"Fixed blocks: {[(pos, b.block_type) for pos, b in board.blocks.items() if b.is_fixed]}")
print(f"Lasers: {board.lasers}")
print(f"Targets: {board.target_points}")
print(f"Valid positions: {board.get_valid_positions()}")

visualize_laser_path(board)

# Try a specific configuration
print("\n" + "="*60)
print("Testing with B blocks at (3,1), (3,3), (5,1)")
print("="*60)

board.place_block('B', (3, 1))
board.place_block('B', (3, 3))
board.place_block('B', (5, 1))

visualize_laser_path(board)

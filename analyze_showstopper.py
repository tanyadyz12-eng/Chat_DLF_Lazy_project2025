"""
Detailed analysis of showstopper_4.bff
Let's manually test different configurations
"""

from lazor_solver import BFFParser
from visual_debug import visualize_laser_path

print("="*60)
print("SHOWSTOPPER_4 Analysis")
print("="*60)

board = BFFParser.parse_file('showstopper_4.bff')
print(f"\nBoard: {board.width}x{board.height}")
print(f"Blocks to place: {board.available_blocks}")  # A=3, B=3
print(f"Fixed blocks: {[(pos, b.block_type) for pos, b in board.blocks.items() if b.is_fixed]}")
print(f"Laser: Start={board.lasers[0].start_pos}, Dir={board.lasers[0].direction}")
print(f"Target: {board.target_points}")  # (2, 3)
print(f"Valid positions: {board.get_valid_positions()}")

# Initial state
print("\n" + "="*60)
print("Initial state (no movable blocks):")
print("="*60)
visualize_laser_path(board)

# The laser starts at (3,6) going (-1,-1) [left and up]
# Target is at (2,3)
# Without blocks: (3,6) -> (2,5) -> (1,4) -> (0,3) -> exits
# We need to redirect the laser to hit (2,3)

# Let's try placing an A block to reflect the laser
configurations = [
    # Try reflect block at (3,3) to bounce laser
    {(3, 3): 'A'},
    # Try reflect at (5,3)
    {(5, 3): 'A'},
    # Try reflect at (3,5)
    {(3, 5): 'A'},
    # Try multiple blocks
    {(5, 5): 'A', (5, 3): 'A'},
    {(3, 5): 'A', (5, 5): 'A'},
    # Try with opaque to block, then reflect
    {(1, 5): 'B', (3, 5): 'A'},
    {(3, 5): 'A', (5, 5): 'A', (5, 3): 'A'},
]

for i, config in enumerate(configurations):
    board = BFFParser.parse_file('showstopper_4.bff')
    print(f"\n{'='*60}")
    print(f"Config {i+1}: {config}")
    print("="*60)

    for pos, block_type in config.items():
        board.place_block(block_type, pos)

    visualize_laser_path(board)

    hit_points = board.simulate_lasers()
    print(f"Target hit: {(2,3) in hit_points}")

    if (2, 3) in hit_points:
        print("\n*** SOLUTION FOUND! ***")
        print(f"Blocks: {config}")
        break

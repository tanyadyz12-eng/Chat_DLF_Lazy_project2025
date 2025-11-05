"""
Analyze laser configurations across all puzzles
"""

from lazor_solver import BFFParser
import os

print("="*70)
print("LASER CONFIGURATION ANALYSIS")
print("="*70)

bff_files = sorted([f for f in os.listdir('.') if f.endswith('.bff')])

laser_data = []

for bff_file in bff_files:
    board = BFFParser.parse_file(bff_file)

    print(f"\n{bff_file}")
    print("-" * 70)
    print(f"Board size: {board.width}×{board.height}")
    print(f"Number of lasers: {len(board.lasers)}")

    for i, laser in enumerate(board.lasers, 1):
        start = laser.start_pos
        direction = laser.direction

        # Interpret direction
        dir_x = "right" if direction[0] > 0 else "left" if direction[0] < 0 else "none"
        dir_y = "down" if direction[1] > 0 else "up" if direction[1] < 0 else "none"

        print(f"  Laser {i}:")
        print(f"    Start position: {start}")
        print(f"    Direction: {direction} ({dir_x}, {dir_y})")
        print(f"    Grid edge: ", end="")

        # Determine which edge the laser starts from
        max_x = board.width * 2
        max_y = board.height * 2

        edges = []
        if start[0] == 0:
            edges.append("LEFT edge")
        elif start[0] >= max_x:
            edges.append("RIGHT edge")

        if start[1] == 0:
            edges.append("TOP edge")
        elif start[1] >= max_y:
            edges.append("BOTTOM edge")

        print(", ".join(edges) if edges else "Inside board")

    print(f"  Targets: {len(board.target_points)} point(s)")
    print(f"    Positions: {sorted(board.target_points)}")

    laser_data.append({
        'file': bff_file,
        'board_size': (board.width, board.height),
        'num_lasers': len(board.lasers),
        'lasers': [(l.start_pos, l.direction) for l in board.lasers],
        'num_targets': len(board.target_points)
    })

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("\nLaser Count Distribution:")
laser_counts = {}
for data in laser_data:
    count = data['num_lasers']
    laser_counts[count] = laser_counts.get(count, 0) + 1

for count in sorted(laser_counts.keys()):
    puzzles = [d['file'] for d in laser_data if d['num_lasers'] == count]
    print(f"  {count} laser(s): {laser_counts[count]} puzzle(s)")
    for p in puzzles:
        print(f"    - {p}")

print("\nLaser Starting Positions:")
print("  (All coordinates shown as (x, y))")
all_starts = set()
for data in laser_data:
    for start, _ in data['lasers']:
        all_starts.add(start)

print(f"  Unique starting positions: {len(all_starts)}")
for pos in sorted(all_starts):
    puzzles = [d['file'] for d in laser_data
               if any(start == pos for start, _ in d['lasers'])]
    print(f"    {pos}: {', '.join(puzzles)}")

print("\nLaser Directions Used:")
all_dirs = set()
for data in laser_data:
    for _, direction in data['lasers']:
        all_dirs.add(direction)

print(f"  Unique directions: {len(all_dirs)}")
for direction in sorted(all_dirs):
    dir_name = []
    if direction[0] > 0:
        dir_name.append("→ right")
    elif direction[0] < 0:
        dir_name.append("← left")

    if direction[1] > 0:
        dir_name.append("↓ down")
    elif direction[1] < 0:
        dir_name.append("↑ up")

    puzzles = [d['file'] for d in laser_data
               if any(d == direction for _, d in d['lasers'])]

    print(f"    {direction} ({', '.join(dir_name)}): {', '.join(puzzles)}")

print("\n" + "="*70)

"""
Exhaustive search for showstopper_4
Try more combinations systematically
"""

from lazor_solver import BFFParser
import itertools

board_template = BFFParser.parse_file('showstopper_4.bff')
valid_pos = board_template.get_valid_positions()

print(f"Valid positions: {valid_pos}")
print(f"Need to place: 3 A blocks and 3 B blocks")
print(f"Target: (2, 3)")
print()

# Let's try smaller subsets first - maybe we don't need all 6 blocks
# Try with just 1-3 blocks

solutions = []

print("Searching with 1 block...")
for pos in valid_pos:
    for block_type in ['A', 'B']:
        board = BFFParser.parse_file('showstopper_4.bff')
        board.place_block(block_type, pos)
        hit_points = board.simulate_lasers()
        if (2, 3) in hit_points:
            solution = {pos: block_type}
            solutions.append(solution)
            print(f"  FOUND: {solution}")

print(f"\nSearching with 2 blocks...")
for pos1, pos2 in itertools.combinations(valid_pos, 2):
    for b1, b2 in itertools.product(['A', 'B'], repeat=2):
        board = BFFParser.parse_file('showstopper_4.bff')
        board.place_block(b1, pos1)
        board.place_block(b2, pos2)
        hit_points = board.simulate_lasers()
        if (2, 3) in hit_points:
            solution = {pos1: b1, pos2: b2}
            solutions.append(solution)
            print(f"  FOUND: {solution}")

print(f"\nSearching with 3 blocks...")
for pos_combo in itertools.combinations(valid_pos, 3):
    for blocks in itertools.product(['A', 'B'], repeat=3):
        board = BFFParser.parse_file('showstopper_4.bff')
        for pos, block_type in zip(pos_combo, blocks):
            board.place_block(block_type, pos)
        hit_points = board.simulate_lasers()
        if (2, 3) in hit_points:
            solution = dict(zip(pos_combo, blocks))
            solutions.append(solution)
            print(f"  FOUND: {solution}")

if solutions:
    print(f"\n{'='*60}")
    print(f"Found {len(solutions)} solution(s)!")
    print("="*60)

    # Show the first solution in detail
    from visual_debug import visualize_laser_path
    board = BFFParser.parse_file('showstopper_4.bff')
    for pos, block_type in solutions[0].items():
        board.place_block(block_type, pos)

    print(f"\nFirst solution: {solutions[0]}")
    visualize_laser_path(board)
else:
    print("\nNo solution found with 1-3 blocks. Trying more...")

    print(f"\nSearching with 4 blocks...")
    count = 0
    for pos_combo in itertools.combinations(valid_pos, 4):
        for blocks in itertools.product(['A', 'B'], repeat=4):
            count += 1
            if count % 100 == 0:
                print(f"  Checked {count} configurations...")
            board = BFFParser.parse_file('showstopper_4.bff')
            for pos, block_type in zip(pos_combo, blocks):
                board.place_block(block_type, pos)
            hit_points = board.simulate_lasers()
            if (2, 3) in hit_points:
                solution = dict(zip(pos_combo, blocks))
                solutions.append(solution)
                print(f"  FOUND: {solution}")
                break
        if solutions:
            break

    if solutions:
        print(f"\n{'='*60}")
        print(f"Found solution with 4 blocks!")
        print("="*60)

        from visual_debug import visualize_laser_path
        board = BFFParser.parse_file('showstopper_4.bff')
        for pos, block_type in solutions[0].items():
            board.place_block(block_type, pos)

        print(f"\nSolution: {solutions[0]}")
        visualize_laser_path(board)

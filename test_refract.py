"""
Test the C (refract) block behavior to verify correctness
"""

from lazor_solver import Block

print("="*70)
print("REFRACT BLOCK (C) BEHAVIOR TEST")
print("="*70)

# Create a refract block
refract_block = Block('C', (3, 3))

print("\nCurrent Implementation:")
print("-" * 70)
print("When a laser hits a refract block, it should:")
print("  According to Lazor game mechanics:")
print("    1. Pass through (continue in same direction)")
print("    2. AND also create a reflected beam (90-degree bounce)")
print()

# Test different edge hits
test_cases = [
    ('left', (1, 1), "Laser going right-down hits LEFT edge"),
    ('right', (1, 1), "Laser going right-down hits RIGHT edge"),
    ('top', (1, 1), "Laser going right-down hits TOP edge"),
    ('bottom', (1, 1), "Laser going right-down hits BOTTOM edge"),
]

for edge, laser_dir, description in test_cases:
    print(f"\nTest: {description}")
    print(f"  Laser direction: {laser_dir}")
    print(f"  Edge hit: {edge}")

    new_directions = refract_block.interact_with_laser(edge, laser_dir)

    print(f"  Result: {len(new_directions)} beam(s)")
    for i, direction in enumerate(new_directions, 1):
        print(f"    Beam {i}: direction {direction}")

print("\n" + "="*70)
print("QUESTION FOR USER:")
print("="*70)
print("""
Is this behavior correct for Lazor's refract block?

Option A (Current implementation):
  - Laser CONTINUES through (transparent)
  - AND creates a REFLECTED beam (90-degree bounce)
  - Result: TWO beams (one continues, one reflects)

Option B (Alternative interpretation):
  - Laser only BENDS/REFRACTS at an angle
  - Result: ONE beam at a new angle

Option C (Pure transmission):
  - Laser just passes through unchanged
  - Result: ONE beam continuing straight

Please clarify which behavior is correct!
""")

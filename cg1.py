"""
Project Setup Script
Run this to create all project files in one go
"""

import os

# README.md content
readme_content = """# Lazor Puzzle Solver

Automatic solver for the Lazor puzzle game. This program reads board configuration files (.bff) and finds solutions by testing different block placements until all target points are hit by lasers.

## Team Members
- Zhihan Liu
- Yizhe Ding
- Qian Fu

## Requirements

- Python 3.7+
- No external libraries required (uses only standard library)

## Installation

```bash
git clone [your-repo-url]
cd lazor-solver
```

## Quick Start

### 1. Create test board files:
```bash
python test_boards.py
```

### 2. Solve a board:
```bash
python lazor_solver.py mad_1.bff
```

### 3. Run unit tests:
```bash
python test_lazor_solver.py
```

### 4. Test all boards:
```bash
python test_boards.py test
```

## File Format (.bff)

Board files use the following format:

```
GRID START
o o o o    # o = blocks allowed, x = no blocks allowed
o o o o    # A/B/C = fixed blocks (reflect/opaque/refract)
GRID STOP

A 2        # 2 reflect blocks available
B 1        # 1 opaque block available
C 1        # 1 refract block available

L 2 7 1 -1 # Laser: position (2,7), direction (1,-1)

P 3 0      # Target point at (3,0)
P 4 3      # Target point at (4,3)
```

### Block Types

- **A (Reflect)**: Reflects laser at 90 degrees
- **B (Opaque)**: Absorbs laser completely
- **C (Refract)**: Splits laser into two beams (one continues, one reflects)

### Coordinate System

- Origin (0,0) is at top-left
- Step size is "half blocks" (even = between blocks, odd = at block centers)
- X-axis increases to the right
- Y-axis increases downward

## Project Structure

```
lazor-solver/
├── lazor_solver.py          # Main solver implementation
├── test_boards.py           # Test file creator and batch tester
├── test_lazor_solver.py     # Unit tests
├── setup_project.py         # This setup script
├── README.md               # This file
├── mad_1.bff               # Test board files
├── braid_5.bff
├── test_3.bff
├── test_4.bff
└── *_solution.txt          # Generated solution files
```

## Algorithm

1. **Parse Board**: Read .bff file and extract grid, blocks, lasers, and targets
2. **Generate Configurations**: Create all possible combinations of block placements
3. **Simulate Lasers**: For each configuration, trace laser paths
4. **Check Solution**: Verify if all target points are hit
5. **Output Result**: Save solution to file with visualization

### Optimization Techniques

- **Early Termination**: Skip permutations when all blocks are same type
- **Visited State Tracking**: Avoid infinite loops in laser simulation
- **Efficient Data Structures**: Use sets for fast lookup of hit points

## Output Format

Solutions are saved to `<board_name>_solution.txt` with:

- Block placement details (grid position and laser coordinates)
- Fixed block locations
- Verification of target points
- Visual grid representation

Example output:
```
PLACED BLOCKS:
  1. Reflect (A) at grid[0][1] (laser coords (3, 1))
  2. Reflect (A) at grid[2][2] (laser coords (5, 5))

VISUAL GRID:
  0: . a . .
  1: . . . .
  2: . . a .
  3: . . . .

  (Uppercase = fixed, lowercase = placed)
```

## Code Quality

- **PEP8 Compliant**: Follows Python style guidelines
- **Docstrings**: All functions and classes documented
- **Type Hints**: Clear parameter and return types
- **Error Handling**: Robust file reading and validation

## Contributing

This is a class project for EN.540.635 Software Carpentry at Johns Hopkins University.

## License

Educational use only - Johns Hopkins University ChemBE Department

## Acknowledgments

- Course Instructors: V. Matos, L. Oluoch, T. Mellor
- Original Lazor game creators
"""

# .gitignore content
gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Output files
*_solution.txt

# OS
.DS_Store
Thumbs.db

# Test files
.pytest_cache/
.coverage
htmlcov/
"""


def create_file(filename, content):
    """Create a file with given content."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {filename}")


def main():
    """Create all project files."""
    print("=" * 60)
    print("LAZOR SOLVER PROJECT SETUP")
    print("=" * 60)
    print()

    # Check if main files already exist
    files_to_check = ['lazor_solver.py', 'test_boards.py', 'test_lazor_solver.py']
    existing = [f for f in files_to_check if os.path.exists(f)]

    if existing:
        print("⚠️  Warning: The following files already exist:")
        for f in existing:
            print(f"   - {f}")
        response = input("\nOverwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
        print()

    # Create README
    create_file('README.md', readme_content)

    # Create .gitignore
    create_file('.gitignore', gitignore_content)

    print()
    print("=" * 60)
    print("✓ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Make sure you have lazor_solver.py in this directory")
    print("  2. Make sure you have test_boards.py in this directory")
    print("  3. Make sure you have test_lazor_solver.py in this directory")
    print("  4. Run: python test_boards.py")
    print("  5. Run: python lazor_solver.py mad_1.bff")
    print()
    print("Files created:")
    print("  - README.md")
    print("  - .gitignore")
    print()


if __name__ == "__main__":
    main()
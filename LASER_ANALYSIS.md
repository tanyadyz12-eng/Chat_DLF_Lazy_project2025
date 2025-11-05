# Laser Configuration Summary

## Overview: Lasers Vary Greatly!

Each puzzle has a **unique laser configuration**. Here's the breakdown:

## By Number of Lasers

### Single Laser (5 puzzles)
- **mad_1**: 1 laser from bottom-left going ↗ (right, up)
- **mad_4**: 1 laser from right going ↙ (left, down)
- **showstopper_4**: 1 laser from bottom going ↖ (left, up)
- **tiny_5**: 1 laser from middle going ↖ (left, up)
- **yarn_5**: 1 laser from top going ↘ (right, down)

### Two Lasers (2 puzzles)
- **mad_7**: 2 lasers from different sides
  - Laser 1: (2,1) going ↘ (right, down)
  - Laser 2: (9,4) going ↙ (left, down)

- **numbered_6**: 2 lasers from bottom
  - Laser 1: (4,9) going ↖ (left, up)
  - Laser 2: (6,9) going ↖ (left, up)

### Four Lasers (1 puzzle)
- **dark_1**: Most complex with 4 lasers!
  - Laser 1: (3,0) from TOP going ↙ (left, down)
  - Laser 2: (1,6) from BOTTOM going ↗ (right, up)
  - Laser 3: (3,6) from BOTTOM going ↖ (left, up)
  - Laser 4: (4,3) from MIDDLE going ↗ (right, up)

## Laser Starting Positions

```
12 unique starting positions across all puzzles!

Position    | Puzzle(s)              | Edge Location
------------|------------------------|------------------
(1, 6)      | dark_1                 | Bottom edge
(2, 1)      | mad_7                  | Inside board
(2, 7)      | mad_1                  | Inside board
(3, 0)      | dark_1                 | Top edge
(3, 6)      | dark_1, showstopper_4  | Bottom edge
(4, 1)      | yarn_5                 | Inside board
(4, 3)      | dark_1                 | Inside board
(4, 5)      | tiny_5                 | Inside board
(4, 9)      | numbered_6             | Inside board
(6, 9)      | numbered_6             | Right edge
(7, 2)      | mad_4                  | Inside board
(9, 4)      | mad_7                  | Inside board
```

## Laser Directions Used

Only **4 unique direction vectors** across all puzzles:

### ↖ Left + Up: (-1, -1)
Most common direction!
- **dark_1** (1 of 4 lasers)
- **numbered_6** (both lasers)
- **showstopper_4**
- **tiny_5**

### ↙ Left + Down: (-1, 1)
Second most common
- **dark_1** (1 of 4 lasers)
- **mad_4**
- **mad_7** (1 of 2 lasers)

### ↗ Right + Up: (1, -1)
- **dark_1** (2 of 4 lasers)
- **mad_1**

### ↘ Right + Down: (1, 1)
- **mad_7** (1 of 2 lasers)
- **yarn_5**

## Interesting Patterns

### 1. Dark_1 is Special
- **Only puzzle with 4 lasers**
- Uses 3 of the 4 possible directions
- Has lasers starting from both edges AND inside
- Most complex laser configuration!

### 2. Direction Preference
The **diagonal up-left (↖)** direction is most popular, used in 4 puzzles

### 3. Starting Positions
- Most lasers start **inside the board** (not on edges)
- Only **dark_1** and **numbered_6** have lasers starting from grid edges
- Position (3, 6) is shared by 2 puzzles: dark_1 and showstopper_4

### 4. Symmetry
- **numbered_6**: Both lasers go in the same direction (↖)
- **mad_7**: Both lasers have downward component but different horizontal

## Visual Representation

```
Direction Compass:
     ↖(-1,-1)    ↗(1,-1)
         ╲      ╱
          ╲    ╱
           ╲  ╱
            \/
            /\
           /  \
          /    \
         ╱      ╲
     ↙(-1,1)    ↘(1,1)
```

## Summary Statistics

- **Total puzzles**: 8
- **Total laser instances**: 12 (across all puzzles)
- **Unique starting positions**: 12 (every laser is unique!)
- **Unique directions**: 4 (all diagonal movements)
- **Puzzles with 1 laser**: 5 (62.5%)
- **Puzzles with 2 lasers**: 2 (25%)
- **Puzzles with 4 lasers**: 1 (12.5%)
- **Average lasers per puzzle**: 1.5

## Key Takeaway

**NO two puzzles have identical laser configurations!** Each puzzle is unique in:
- Number of lasers
- Starting positions
- Movement directions
- Combination of the above

This variety makes each puzzle a distinct challenge requiring different blocking strategies!

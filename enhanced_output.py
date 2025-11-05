"""
Enhanced solution writer with JSON, TXT, and PNG output formats
"""

import json
import os
from typing import Dict, Tuple
from lazor_solver import Board

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not available. PNG output will be disabled.")
    print("Install with: pip install Pillow")


class EnhancedSolutionWriter:
    """
    Writes solutions in multiple formats: JSON, TXT, PNG
    """

    def __init__(self, output_dir: str = "solutions"):
        """
        Initialize the writer with output directory.

        Args:
            output_dir: Directory to save solution files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def write_json_solution(self, filename: str, board: Board,
                           solution: Dict[Tuple[int, int], str],
                           solve_time: float):
        """
        Write solution to JSON file.

        Args:
            filename: Base filename (without extension)
            board: Board object
            solution: Solution dictionary
            solve_time: Time taken to solve
        """
        # Convert solution keys to strings (JSON doesn't support tuple keys)
        solution_serializable = {
            f"{k[0]},{k[1]}": v for k, v in solution.items()
        }

        # Get laser paths
        hit_points = board.simulate_lasers()
        hit_points_list = [list(p) for p in sorted(hit_points)]

        # Build JSON structure
        data = {
            "puzzle_name": filename,
            "board": {
                "width": board.width,
                "height": board.height,
                "grid": board.grid
            },
            "available_blocks": board.available_blocks,
            "lasers": [
                {
                    "start": list(laser.start_pos),
                    "direction": list(laser.direction)
                }
                for laser in board.lasers
            ],
            "target_points": [list(p) for p in sorted(board.target_points)],
            "solution": {
                "blocks_placed": solution_serializable,
                "num_blocks": len(solution),
                "grid_positions": [
                    {
                        "block_type": block_type,
                        "laser_coords": [int(pos.split(',')[0]), int(pos.split(',')[1])],
                        "grid_coords": [
                            (int(pos.split(',')[0]) - 1) // 2,
                            (int(pos.split(',')[1]) - 1) // 2
                        ]
                    }
                    for pos, block_type in solution_serializable.items()
                ]
            },
            "verification": {
                "targets_hit": [list(p) for p in sorted(board.target_points.intersection(hit_points))],
                "all_hit_points": hit_points_list,
                "is_solved": board.check_solution()
            },
            "performance": {
                "solve_time_seconds": round(solve_time, 4)
            }
        }

        # Write to file
        output_path = os.path.join(self.output_dir, f"{filename}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        return output_path

    def write_text_solution(self, filename: str, board: Board,
                           solution: Dict[Tuple[int, int], str],
                           solve_time: float):
        """
        Write solution to text file.

        Args:
            filename: Base filename (without extension)
            board: Board object
            solution: Solution dictionary
            solve_time: Time taken to solve
        """
        output_path = os.path.join(self.output_dir, f"{filename}.txt")

        with open(output_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write(f"LAZOR BOARD SOLUTION: {filename}\n")
            f.write("="*60 + "\n\n")

            # Board configuration
            f.write("Board Configuration:\n")
            f.write("-" * 40 + "\n")
            for row_idx in range(board.height):
                row_str = ""
                for col_idx in range(board.width):
                    pos = (col_idx * 2 + 1, row_idx * 2 + 1)

                    if pos in board.blocks:
                        block = board.blocks[pos]
                        if block.is_fixed:
                            row_str += f"[{block.block_type}] "
                        else:
                            row_str += f" {block.block_type}  "
                    elif board.grid[row_idx][col_idx] == 'o':
                        row_str += " .  "
                    else:
                        row_str += " x  "

                f.write("  " + row_str + "\n")

            # Legend
            f.write("\nLegend:\n")
            f.write("  [X] = Fixed block\n")
            f.write("   X  = Placed block\n")
            f.write("   .  = Empty position\n")
            f.write("   x  = No block allowed\n")

            # Block placement details
            f.write("\n" + "="*60 + "\n")
            f.write("Block Placement Details:\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Blocks available: {board.available_blocks}\n")
            f.write(f"  Blocks placed: {len(solution)}\n\n")

            for pos, block_type in sorted(solution.items()):
                grid_x = (pos[0] - 1) // 2
                grid_y = (pos[1] - 1) // 2
                f.write(f"  [{block_type}] Block at grid ({grid_x}, {grid_y})")
                f.write(f" → laser coords ({pos[0]}, {pos[1]})\n")

            # Laser information
            f.write("\n" + "="*60 + "\n")
            f.write("Laser Configuration:\n")
            f.write("-" * 40 + "\n")
            for i, laser in enumerate(board.lasers, 1):
                f.write(f"  Laser {i}: Start {laser.start_pos}, ")
                f.write(f"Direction {laser.direction}\n")

            # Target verification
            f.write("\n" + "="*60 + "\n")
            f.write("Target Verification:\n")
            f.write("-" * 40 + "\n")
            hit_points = board.simulate_lasers()
            for point in sorted(board.target_points):
                status = "[+] HIT " if point in hit_points else "[-] MISS"
                f.write(f"  {status} Target at {point}\n")

            # Summary
            f.write("\n" + "="*60 + "\n")
            f.write("Summary:\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Solution Status: {'SOLVED' if board.check_solution() else 'NOT SOLVED'}\n")
            f.write(f"  Solve Time: {solve_time:.4f} seconds\n")
            f.write(f"  Targets Hit: {len(board.target_points.intersection(hit_points))}/{len(board.target_points)}\n")
            f.write("="*60 + "\n")

        return output_path

    def write_png_solution(self, filename: str, board: Board,
                          solution: Dict[Tuple[int, int], str],
                          solve_time: float):
        """
        Write solution as PNG image.

        Args:
            filename: Base filename (without extension)
            board: Board object
            solution: Solution dictionary
            solve_time: Time taken to solve
        """
        if not HAS_PIL:
            print(f"Skipping PNG generation for {filename} (PIL not available)")
            return None

        # Configuration
        CELL_SIZE = 60
        MARGIN = 80
        LASER_SCALE = 2  # Laser grid is 2x the block grid

        # Calculate dimensions
        img_width = board.width * CELL_SIZE + 2 * MARGIN
        img_height = board.height * CELL_SIZE + 2 * MARGIN + 100  # Extra space for info

        # Create image
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        # Colors
        COLOR_GRID = (200, 200, 200)
        COLOR_BLOCK_REFLECT = (100, 150, 255)
        COLOR_BLOCK_OPAQUE = (80, 80, 80)
        COLOR_BLOCK_REFRACT = (255, 150, 100)
        COLOR_FIXED = (255, 0, 0)
        COLOR_LASER = (255, 0, 255)
        COLOR_TARGET = (0, 200, 0)
        COLOR_TARGET_HIT = (0, 255, 0)
        COLOR_TARGET_MISS = (255, 0, 0)
        COLOR_TEXT = (0, 0, 0)

        # Draw grid
        for row in range(board.height):
            for col in range(board.width):
                x = MARGIN + col * CELL_SIZE
                y = MARGIN + row * CELL_SIZE

                # Draw cell border
                draw.rectangle([x, y, x + CELL_SIZE, y + CELL_SIZE],
                             outline=COLOR_GRID, width=1)

                # Check if blocked position
                if board.grid[row][col] == 'x':
                    # Draw X pattern
                    draw.line([x, y, x + CELL_SIZE, y + CELL_SIZE],
                            fill=COLOR_GRID, width=2)
                    draw.line([x + CELL_SIZE, y, x, y + CELL_SIZE],
                            fill=COLOR_GRID, width=2)

        # Draw blocks
        for pos, block in board.blocks.items():
            grid_x = (pos[0] - 1) // 2
            grid_y = (pos[1] - 1) // 2

            x = MARGIN + grid_x * CELL_SIZE + 5
            y = MARGIN + grid_y * CELL_SIZE + 5
            w = CELL_SIZE - 10
            h = CELL_SIZE - 10

            # Choose color
            if block.block_type == 'A':
                color = COLOR_BLOCK_REFLECT
            elif block.block_type == 'B':
                color = COLOR_BLOCK_OPAQUE
            else:  # C
                color = COLOR_BLOCK_REFRACT

            # Draw block
            draw.rectangle([x, y, x + w, y + h], fill=color, outline=COLOR_TEXT, width=2)

            # Draw block label
            label = block.block_type
            if block.is_fixed:
                label = f"[{label}]"

            # Try to use a font, fall back to default
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()

            # Get text size and center it
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = x + (w - text_width) // 2
            text_y = y + (h - text_height) // 2

            draw.text((text_x, text_y), label, fill='white' if block.block_type == 'B' else COLOR_TEXT, font=font)

        # Draw laser paths
        hit_points = board.simulate_lasers()
        for point in hit_points:
            lx, ly = point
            # Convert laser coordinates to pixel coordinates
            # Laser coordinate space is 2x the grid
            px = MARGIN + (lx * CELL_SIZE) // 2 - 3
            py = MARGIN + (ly * CELL_SIZE) // 2 - 3

            draw.ellipse([px, py, px + 6, py + 6], fill=COLOR_LASER)

        # Draw laser start points
        for laser in board.lasers:
            lx, ly = laser.start_pos
            px = MARGIN + (lx * CELL_SIZE) // 2 - 5
            py = MARGIN + (ly * CELL_SIZE) // 2 - 5

            draw.ellipse([px, py, px + 10, py + 10], fill=(255, 255, 0), outline=COLOR_TEXT, width=2)

        # Draw target points
        for target in board.target_points:
            tx, ty = target
            px = MARGIN + (tx * CELL_SIZE) // 2 - 8
            py = MARGIN + (ty * CELL_SIZE) // 2 - 8

            color = COLOR_TARGET_HIT if target in hit_points else COLOR_TARGET_MISS
            draw.rectangle([px, py, px + 16, py + 16], outline=color, width=3)
            draw.line([px, py, px + 16, py + 16], fill=color, width=2)
            draw.line([px + 16, py, px, py + 16], fill=color, width=2)

        # Draw info at bottom
        info_y = MARGIN + board.height * CELL_SIZE + 20

        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_title = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            font_title = font

        # Title
        draw.text((MARGIN, info_y), f"Solution: {filename}", fill=COLOR_TEXT, font=font_title)
        info_y += 30

        # Info
        status = "SOLVED" if board.check_solution() else "NOT SOLVED"
        info_text = [
            f"Status: {status}",
            f"Time: {solve_time:.4f}s",
            f"Blocks placed: {len(solution)}",
            f"Targets: {len(board.target_points.intersection(hit_points))}/{len(board.target_points)} hit"
        ]

        for line in info_text:
            draw.text((MARGIN, info_y), line, fill=COLOR_TEXT, font=font)
            info_y += 20

        # Legend at bottom
        legend_y = info_y + 10
        legend_items = [
            ("○", COLOR_LASER, "Laser path"),
            ("☐", COLOR_TARGET_HIT, "Target hit"),
            ("☐", COLOR_TARGET_MISS, "Target miss"),
        ]

        legend_x = MARGIN
        for symbol, color, text in legend_items:
            draw.text((legend_x, legend_y), symbol, fill=color, font=font)
            draw.text((legend_x + 20, legend_y), text, fill=COLOR_TEXT, font=font)
            legend_x += 150

        # Save image
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        img.save(output_path)

        return output_path

    def write_all_formats(self, filename: str, board: Board,
                         solution: Dict[Tuple[int, int], str],
                         solve_time: float):
        """
        Write solution in all available formats.

        Args:
            filename: Base filename (without extension)
            board: Board object
            solution: Solution dictionary
            solve_time: Time taken to solve

        Returns:
            Dictionary with paths to generated files
        """
        results = {}

        # JSON
        try:
            results['json'] = self.write_json_solution(filename, board, solution, solve_time)
            print(f"  JSON: {results['json']}")
        except Exception as e:
            print(f"  Error writing JSON: {e}")

        # TXT
        try:
            results['txt'] = self.write_text_solution(filename, board, solution, solve_time)
            print(f"  TXT:  {results['txt']}")
        except Exception as e:
            print(f"  Error writing TXT: {e}")

        # PNG
        try:
            results['png'] = self.write_png_solution(filename, board, solution, solve_time)
            if results['png']:
                print(f"  PNG:  {results['png']}")
        except Exception as e:
            print(f"  Error writing PNG: {e}")

        return results

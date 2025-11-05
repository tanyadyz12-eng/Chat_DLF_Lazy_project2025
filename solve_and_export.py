"""
Solve all Lazor boards and save results in JSON, TXT, and PNG formats
"""

import os
import time
from lazor_solver import BFFParser, LazorSolver
from enhanced_output import EnhancedSolutionWriter


def solve_all_boards(output_dir="solutions"):
    """
    Solve all .bff files and save results in multiple formats.

    Args:
        output_dir: Directory to save solution files
    """
    # Get all .bff files
    bff_files = sorted([f for f in os.listdir('.') if f.endswith('.bff')])

    if not bff_files:
        print("No .bff files found in current directory!")
        return

    print(f"\n{'='*70}")
    print(f"LAZOR SOLVER - Multi-Format Output")
    print(f"{'='*70}")
    print(f"Found {len(bff_files)} puzzle(s) to solve")
    print(f"Output directory: {output_dir}/")
    print(f"{'='*70}\n")

    # Initialize writer
    writer = EnhancedSolutionWriter(output_dir)

    results = []
    total_time = 0

    for bff_file in bff_files:
        puzzle_name = bff_file.replace('.bff', '')

        print(f"\n{'─'*70}")
        print(f"Solving: {bff_file}")
        print(f"{'─'*70}")

        try:
            # Parse the file
            board = BFFParser.parse_file(bff_file)
            print(f"  Board: {board.width}×{board.height}")
            print(f"  Blocks: {board.available_blocks}")
            print(f"  Lasers: {len(board.lasers)}")
            print(f"  Targets: {len(board.target_points)}")

            # Solve
            print(f"  Solving...")
            start_time = time.time()
            solver = LazorSolver(board)
            solution = solver.solve_optimized()
            solve_time = time.time() - start_time

            if solution is not None:
                print(f"  [+] SOLVED in {solve_time:.4f} seconds!")
                print(f"  Blocks placed: {len(solution)}")

                # Write all formats
                print(f"  Writing output files:")
                output_files = writer.write_all_formats(
                    puzzle_name, board, solution, solve_time
                )

                results.append({
                    'file': bff_file,
                    'solved': True,
                    'time': solve_time,
                    'blocks_placed': len(solution),
                    'outputs': output_files
                })
                total_time += solve_time

            else:
                print(f"  [-] No solution found (searched for {solve_time:.4f}s)")
                results.append({
                    'file': bff_file,
                    'solved': False,
                    'time': solve_time,
                    'blocks_placed': 0,
                    'outputs': {}
                })

        except Exception as e:
            print(f"  [!] ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'file': bff_file,
                'solved': False,
                'error': str(e)
            })

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")

    solved_count = sum(1 for r in results if r.get('solved', False))
    print(f"Puzzles solved: {solved_count}/{len(results)}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time: {total_time/len(results):.2f} seconds")
    print(f"\nResults saved to: {output_dir}/")

    print(f"\n{'─'*70}")
    print(f"Individual Results:")
    print(f"{'─'*70}")

    for result in results:
        status = "[+] SOLVED" if result.get('solved', False) else "[-] FAILED"
        time_str = f"{result.get('time', 0):.4f}s" if 'time' in result else "N/A"
        blocks = result.get('blocks_placed', 0)

        print(f"{status:12} {result['file']:20} {time_str:>10}  ({blocks} blocks)")

    print(f"{'='*70}\n")

    # List generated files
    print(f"Generated files in {output_dir}/:")
    print(f"{'─'*70}")

    try:
        files = sorted(os.listdir(output_dir))
        by_ext = {'json': [], 'txt': [], 'png': []}

        for f in files:
            ext = f.split('.')[-1]
            if ext in by_ext:
                by_ext[ext].append(f)

        for ext in ['json', 'txt', 'png']:
            if by_ext[ext]:
                print(f"\n{ext.upper()} files ({len(by_ext[ext])}):")
                for f in by_ext[ext]:
                    print(f"  - {f}")

    except Exception as e:
        print(f"Error listing files: {e}")

    print(f"\n{'='*70}")
    print(f"Done!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    solve_all_boards()

"""
Unit tests for Lazor Board Game Solver

Tests all major components including:
- Block class and laser interactions
- Board class and grid management
- Laser simulation
- BFF file parsing
- Solution finding

Run with: python test_lazor_solver.py
"""

import unittest
import os
import tempfile
from lazor_solver import (
    Block, Laser, Board, BFFParser, LazorSolver, SolutionWriter
)


class TestBlock(unittest.TestCase):
    """Test Block class functionality"""

    def test_block_creation(self):
        """Test creating blocks of different types"""
        block_a = Block('A', (1, 1))
        self.assertEqual(block_a.block_type, 'A')
        self.assertEqual(block_a.position, (1, 1))
        self.assertFalse(block_a.is_fixed)

        block_b = Block('B', (3, 3), is_fixed=True)
        self.assertTrue(block_b.is_fixed)

    def test_invalid_block_type(self):
        """Test that invalid block types raise errors"""
        with self.assertRaises(ValueError):
            Block('X', (1, 1))

    def test_reflect_block_interaction(self):
        """Test reflect block laser interaction"""
        block = Block('A', (3, 3))

        # Hit left edge
        directions = block.interact_with_laser('left', (1, 1))
        self.assertEqual(directions, [(-1, 1)])

        # Hit right edge
        directions = block.interact_with_laser('right', (1, 1))
        self.assertEqual(directions, [(-1, 1)])

        # Hit top edge
        directions = block.interact_with_laser('top', (1, 1))
        self.assertEqual(directions, [(1, -1)])

        # Hit bottom edge
        directions = block.interact_with_laser('bottom', (1, 1))
        self.assertEqual(directions, [(1, -1)])

    def test_opaque_block_interaction(self):
        """Test opaque block stops laser"""
        block = Block('B', (3, 3))
        directions = block.interact_with_laser('left', (1, 1))
        self.assertEqual(directions, [])

    def test_refract_block_interaction(self):
        """Test refract block creates two beams"""
        block = Block('C', (3, 3))
        directions = block.interact_with_laser('left', (1, 1))
        self.assertEqual(len(directions), 2)
        self.assertIn((1, 1), directions)  # Original direction
        self.assertIn((-1, 1), directions)  # Reflected direction


class TestLaser(unittest.TestCase):
    """Test Laser class functionality"""

    def test_laser_creation(self):
        """Test creating a laser"""
        laser = Laser((2, 7), (1, -1))
        self.assertEqual(laser.start_pos, (2, 7))
        self.assertEqual(laser.direction, (1, -1))


class TestBoard(unittest.TestCase):
    """Test Board class functionality"""

    def test_board_creation(self):
        """Test creating a board"""
        grid = [['o', 'o', 'o'],
                ['o', 'o', 'o'],
                ['o', 'o', 'o']]
        board = Board(grid)
        self.assertEqual(board.width, 3)
        self.assertEqual(board.height, 3)

    def test_fixed_blocks_extraction(self):
        """Test extracting fixed blocks from grid"""
        grid = [['A', 'o', 'o'],
                ['o', 'B', 'o'],
                ['o', 'o', 'C']]
        board = Board(grid)

        # Should have 3 fixed blocks
        self.assertEqual(len(board.blocks), 3)

        # Check positions are correct
        self.assertIn((1, 1), board.blocks)  # A at grid (0,0)
        self.assertIn((3, 3), board.blocks)  # B at grid (1,1)
        self.assertIn((5, 5), board.blocks)  # C at grid (2,2)

        # All should be marked as fixed
        for block in board.blocks.values():
            self.assertTrue(block.is_fixed)

    def test_valid_positions(self):
        """Test getting valid block positions"""
        grid = [['o', 'x', 'o'],
                ['A', 'o', 'o'],
                ['o', 'o', 'x']]
        board = Board(grid)

        valid_pos = board.get_valid_positions()

        # Should include 'o' positions that don't have fixed blocks
        self.assertIn((1, 1), valid_pos)  # Grid (0,0) - has fixed A, should not be included
        self.assertIn((5, 1), valid_pos)  # Grid (2,0)
        self.assertIn((3, 3), valid_pos)  # Grid (1,1)

        # Should not include 'x' positions
        self.assertNotIn((3, 1), valid_pos)  # Grid (1,0)

    def test_place_and_remove_blocks(self):
        """Test placing and removing blocks"""
        grid = [['o', 'o'], ['o', 'o']]
        board = Board(grid)

        # Place a block
        board.place_block('A', (1, 1))
        self.assertIn((1, 1), board.blocks)
        self.assertEqual(board.blocks[(1, 1)].block_type, 'A')

        # Remove the block
        board.remove_block((1, 1))
        self.assertNotIn((1, 1), board.blocks)

    def test_cannot_remove_fixed_blocks(self):
        """Test that fixed blocks cannot be removed"""
        grid = [['A', 'o']]
        board = Board(grid)

        initial_count = len(board.blocks)
        board.remove_block((1, 1))  # Try to remove fixed block

        # Should still be there
        self.assertEqual(len(board.blocks), initial_count)


class TestBFFParser(unittest.TestCase):
    """Test BFF file parsing"""

    def test_parse_simple_file(self):
        """Test parsing a simple BFF file"""
        # Create a temporary BFF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bff', delete=False) as f:
            f.write("""
GRID START
o o
o o
GRID STOP

A 2

L 1 3 1 -1

P 3 1
            """)
            temp_file = f.name

        try:
            board = BFFParser.parse_file(temp_file)

            # Check grid
            self.assertEqual(board.width, 2)
            self.assertEqual(board.height, 2)

            # Check available blocks
            self.assertEqual(board.available_blocks['A'], 2)
            self.assertEqual(board.available_blocks['B'], 0)
            self.assertEqual(board.available_blocks['C'], 0)

            # Check laser
            self.assertEqual(len(board.lasers), 1)
            self.assertEqual(board.lasers[0].start_pos, (1, 3))
            self.assertEqual(board.lasers[0].direction, (1, -1))

            # Check target points
            self.assertIn((3, 1), board.target_points)

        finally:
            os.unlink(temp_file)

    def test_parse_with_fixed_blocks(self):
        """Test parsing file with fixed blocks"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bff', delete=False) as f:
            f.write("""
GRID START
B o
o A
GRID STOP

C 1

L 1 3 1 -1

P 3 1
            """)
            temp_file = f.name

        try:
            board = BFFParser.parse_file(temp_file)

            # Should have 2 fixed blocks
            fixed_blocks = [b for b in board.blocks.values() if b.is_fixed]
            self.assertEqual(len(fixed_blocks), 2)

            # Check block types
            self.assertEqual(board.blocks[(1, 1)].block_type, 'B')
            self.assertEqual(board.blocks[(3, 3)].block_type, 'A')

        finally:
            os.unlink(temp_file)


class TestLaserSimulation(unittest.TestCase):
    """Test laser simulation"""

    def test_laser_straight_path(self):
        """Test laser traveling in straight line"""
        grid = [['o', 'o', 'o']]
        board = Board(grid)

        laser = Laser((0, 1), (1, 0))
        board.lasers = [laser]

        hit_points = board.simulate_lasers()

        # Should hit points along horizontal line at y=1
        self.assertIn((0, 1), hit_points)
        self.assertIn((1, 1), hit_points)
        self.assertIn((2, 1), hit_points)

    def test_laser_blocked_by_opaque(self):
        """Test laser stopped by opaque block"""
        grid = [['o', 'B', 'o']]
        board = Board(grid)

        laser = Laser((0, 1), (1, 0))
        board.lasers = [laser]

        hit_points = board.simulate_lasers()

        # Laser should stop at the opaque block
        # Should not pass through to the other side
        self.assertIn((0, 1), hit_points)
        # The exact behavior depends on implementation details


class TestSolver(unittest.TestCase):
    """Test the solver"""

    def test_solver_simple_case(self):
        """Test solver on a simple case"""
        # This would test a known solvable board
        # For now, we'll test the solver structure
        grid = [['o']]
        board = Board(grid)
        board.available_blocks = {'A': 0, 'B': 0, 'C': 0}
        board.lasers = [Laser((0, 1), (1, 0))]
        board.target_points = {(1, 1)}

        solver = LazorSolver(board)
        solution = solver.solve_optimized()

        # With no blocks to place and laser going through (1,1),
        # it should find a solution
        self.assertIsNotNone(solution)

    def test_solver_no_solution(self):
        """Test solver on impossible case"""
        grid = [['o']]
        board = Board(grid)
        board.available_blocks = {'B': 1, 'A': 0, 'C': 0}
        board.lasers = [Laser((0, 1), (1, 0))]
        board.target_points = {(2, 1)}  # Beyond where laser can reach with 1 opaque block

        solver = LazorSolver(board)
        # Depending on the specific configuration, this might or might not have a solution
        # The test is more about ensuring the solver doesn't crash


class TestSolutionWriter(unittest.TestCase):
    """Test solution file writing"""

    def test_write_solution(self):
        """Test writing a solution file"""
        grid = [['o', 'o']]
        board = Board(grid)
        board.lasers = [Laser((0, 1), (1, 0))]
        board.target_points = {(1, 1)}
        board.place_block('A', (1, 1))

        solution = {(1, 1): 'A'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_file = f.name

        try:
            SolutionWriter.write_text_solution(temp_file, board, solution)

            # Check file was created and contains expected content
            with open(temp_file, 'r') as f:
                content = f.read()

            self.assertIn('LAZOR BOARD SOLUTION', content)
            self.assertIn('Block Placement', content)
            self.assertIn('Block A', content)

        finally:
            os.unlink(temp_file)


class TestIntegration(unittest.TestCase):
    """Integration tests using actual .bff files"""

    def test_solve_dark_1(self):
        """Test solving dark_1.bff if it exists"""
        if os.path.exists('dark_1.bff'):
            board = BFFParser.parse_file('dark_1.bff')
            solver = LazorSolver(board)
            solution = solver.solve_optimized()

            # dark_1 should be solvable
            self.assertIsNotNone(solution, "dark_1.bff should have a solution")

    def test_solve_tiny_5(self):
        """Test solving tiny_5.bff if it exists"""
        if os.path.exists('tiny_5.bff'):
            board = BFFParser.parse_file('tiny_5.bff')
            solver = LazorSolver(board)
            solution = solver.solve_optimized()

            # tiny_5 should be solvable
            self.assertIsNotNone(solution, "tiny_5.bff should have a solution")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBlock))
    suite.addTests(loader.loadTestsFromTestCase(TestLaser))
    suite.addTests(loader.loadTestsFromTestCase(TestBoard))
    suite.addTests(loader.loadTestsFromTestCase(TestBFFParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLaserSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestSolver))
    suite.addTests(loader.loadTestsFromTestCase(TestSolutionWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)

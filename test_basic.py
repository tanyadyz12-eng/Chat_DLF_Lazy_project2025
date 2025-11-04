#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic functionality test module.

Provides simple tests for core functionality.
"""
from __future__ import annotations
import sys
from pathlib import Path
from bff_parser import parse_bff
from simulate_wall import trace
from model import Block, BlockType


def test_bff_parsing():
    """Test .bff file parsing functionality."""
    print("Testing .bff file parsing...")
    try:
        board = parse_bff("../boards/dark_1.bff")
        assert board.rows > 0, "Board should have more than 0 rows"
        assert board.cols > 0, "Board should have more than 0 columns"
        assert len(board.lasers) > 0, "Should have at least one laser"
        assert len(board.targets) > 0, "Should have at least one target"
        print("✅ .bff file parsing test passed")
        return True
    except Exception as e:
        print(f"❌ .bff file parsing test failed: {e}")
        return False


def test_block_creation():
    """Test block class creation."""
    print("Testing block class creation...")
    try:
        block_a = Block(BlockType.REFLECT)
        block_b = Block(BlockType.OPAQUE)
        block_c = Block(BlockType.REFRACT)
        assert block_a.kind == BlockType.REFLECT
        assert block_b.kind == BlockType.OPAQUE
        assert block_c.kind == BlockType.REFRACT
        print("✅ Block class creation test passed")
        return True
    except Exception as e:
        print(f"❌ Block class creation test failed: {e}")
        return False


def test_trace_simulation():
    """Test laser path simulation."""
    print("Testing laser path simulation...")
    try:
        board = parse_bff("../boards/dark_1.bff")
        hits, traj = trace(board, {})
        assert isinstance(hits, set), "hits should be a set type"
        assert isinstance(traj, list), "traj should be a list type"
        print("✅ Laser path simulation test passed")
        return True
    except Exception as e:
        print(f"❌ Laser path simulation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Lazor Solver - Basic Functionality Tests")
    print("=" * 50)
    
    tests = [
        test_bff_parsing,
        test_block_creation,
        test_trace_simulation,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


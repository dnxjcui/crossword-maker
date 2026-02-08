import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.serialize import load_puzzle
from src.gui import run_viewer


def main():
    parser = argparse.ArgumentParser(description="View a saved crossword puzzle")
    parser.add_argument("--puzzle", required=True, help="Path to puzzle JSON")
    args = parser.parse_args()

    puzzle = load_puzzle(args.puzzle)
    run_viewer(puzzle=puzzle)


if __name__ == "__main__":
    main()

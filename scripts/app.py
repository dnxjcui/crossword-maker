import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui import run_viewer


def main():
    parser = argparse.ArgumentParser(description="Interactive crossword generator")
    parser.add_argument("--input", required=True, help="Path to word+hint CSV")
    parser.add_argument("--rows", type=int, default=15, help="Grid rows (default: 15)")
    parser.add_argument("--cols", type=int, default=15, help="Grid cols (default: 15)")
    args = parser.parse_args()

    run_viewer(input_path=args.input, rows=args.rows, cols=args.cols)


if __name__ == "__main__":
    main()

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io import load_wordlist
from src.generator import generate_crossword
from src.clues import extract_clues
from src.serialize import save_puzzle


def main():
    parser = argparse.ArgumentParser(description="Generate a crossword puzzle")
    parser.add_argument("--input", required=True, help="Path to word+hint CSV")
    parser.add_argument("--name", required=True, help="Puzzle name (output filename)")
    parser.add_argument("--rows", type=int, default=15, help="Grid rows (default: 15)")
    parser.add_argument("--cols", type=int, default=15, help="Grid cols (default: 15)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--attempts", type=int, default=200, help="Max attempts (default: 200)")
    args = parser.parse_args()

    entries = load_wordlist(args.input)
    print(f"Loaded {len(entries)} words from {args.input}")

    puzzle = generate_crossword(entries, args.rows, args.cols, seed=args.seed, max_attempts=args.attempts)
    puzzle = extract_clues(puzzle)

    out_path = os.path.join("output", f"{args.name}.json")
    save_puzzle(puzzle, out_path)

    meta = puzzle["metadata"]
    print(f"Saved to {out_path}")
    print(f"  Seed: {puzzle['seed']}")
    print(f"  Placed: {meta['placed']}/{meta['total']} words")
    print(f"  Intersections: {meta['intersections']}")
    print(f"  Score: {meta['score']}")
    print(f"  Time: {meta['runtime_ms']}ms")


if __name__ == "__main__":
    main()

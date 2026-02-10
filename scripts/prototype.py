import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io import load_prototype_wordlist
from src.prototype import run_prototype, print_prototype_summary, save_selected_csv
from src.clues import extract_clues
from src.serialize import save_puzzle


def main():
    parser = argparse.ArgumentParser(
        description="Prototype mode: find the best word combination for a crossword"
    )
    parser.add_argument("--input", required=True, help="Path to prototype input file")
    parser.add_argument("--name", required=True, help="Output name (for prototype_output/<name>.json)")
    parser.add_argument("--rows", type=int, default=15, help="Grid rows (default: 15)")
    parser.add_argument("--cols", type=int, default=15, help="Grid cols (default: 15)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--attempts", type=int, default=50,
                        help="Max attempts per combination (default: 50)")
    args = parser.parse_args()

    proto_entries = load_prototype_wordlist(args.input)
    multi = sum(1 for e in proto_entries if len(e["words"]) > 1)
    print(f"Loaded {len(proto_entries)} entries ({multi} with alternatives)")

    result = run_prototype(
        proto_entries, args.rows, args.cols,
        max_attempts=args.attempts, seed=args.seed,
    )
    result = extract_clues(result)

    out_path = os.path.join("prototype_output", f"{args.name}.json")
    save_puzzle(result, out_path)

    csv_path = os.path.join("prototype_output", f"{args.name}.csv")
    save_selected_csv(result, csv_path)

    print_prototype_summary(result)
    print(f"\nSaved to {out_path}")
    print(f"Selected words CSV: {csv_path}")


if __name__ == "__main__":
    main()

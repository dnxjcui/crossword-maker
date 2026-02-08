import json
import os


def save_puzzle(puzzle, out_path):
    """Save puzzle dict to JSON file, creating directories as needed."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(puzzle, f, indent=2)


def load_puzzle(path):
    """Load puzzle dict from JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

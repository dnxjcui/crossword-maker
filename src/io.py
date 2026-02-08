import re
import sys


def load_wordlist(path):
    """Load word+hint pairs from a CSV file.

    Each line: word,hint (split on first comma; hints may contain commas).
    Words are normalized to uppercase A-Z. Duplicates and short words are rejected.
    """
    entries = []
    seen = set()

    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",", 1)
            if len(parts) < 2:
                continue

            raw_word, hint = parts[0].strip(), parts[1].strip()
            word = re.sub(r"[^A-Z]", "", raw_word.upper())

            if len(word) < 2:
                continue

            if word in seen:
                print(f"WARNING: duplicate word '{word}' skipped", file=sys.stderr)
                continue

            seen.add(word)
            entries.append({"word": word, "hint": hint})

    return entries

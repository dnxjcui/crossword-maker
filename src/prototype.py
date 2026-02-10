import itertools
import os
import time

from src.generator import generate_crossword


def run_prototype(proto_entries, rows, cols, max_attempts=50, seed=None):
    """Evaluate all word combinations and return the highest-scoring crossword.

    proto_entries: list of {"words": [str, ...], "hint": str}
    Returns the best puzzle dict with an added "prototype" key.
    """
    alternatives = [e["words"] for e in proto_entries]
    hints = [e["hint"] for e in proto_entries]
    total_combos = 1
    for alts in alternatives:
        total_combos *= len(alts)

    print(f"Total combinations: {total_combos}")
    print(f"Generating with seed={seed}, attempts={max_attempts}, grid={rows}x{cols}")
    print()

    best_puzzle = None
    best_score = -1
    best_combo_index = -1
    best_combo = None
    evaluated = 0
    skipped = 0
    start = time.perf_counter()

    for i, combo in enumerate(itertools.product(*alternatives)):
        # Skip combinations with duplicate words
        if len(set(combo)) < len(combo):
            skipped += 1
            continue

        entries = [{"word": w, "hint": h} for w, h in zip(combo, hints)]
        puzzle = generate_crossword(entries, rows, cols, seed=seed, max_attempts=max_attempts)
        score = puzzle["metadata"]["score"]
        placed = puzzle["metadata"]["placed"]
        total = puzzle["metadata"]["total"]
        evaluated += 1

        # Build variant summary (only multi-option entries)
        variant_words = [combo[j] for j, alts in enumerate(alternatives) if len(alts) > 1]
        variant_str = ", ".join(variant_words)

        is_best = score > best_score
        marker = " *new best*" if is_best else ""
        print(f"[{i + 1}/{total_combos}]  score={score:.4f}  placed={placed}/{total}  ({variant_str}){marker}")

        if is_best:
            best_puzzle = puzzle
            best_score = score
            best_combo_index = i
            best_combo = combo

    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    # Attach prototype metadata
    selected_words = []
    for j, entry in enumerate(proto_entries):
        selected_words.append({
            "chosen": best_combo[j],
            "alternatives": entry["words"],
            "hint": entry["hint"],
        })

    best_puzzle["prototype"] = {
        "total_combinations": total_combos,
        "evaluated": evaluated,
        "skipped_duplicates": skipped,
        "best_combo_index": best_combo_index,
        "selected_words": selected_words,
        "total_runtime_ms": elapsed_ms,
    }

    return best_puzzle


def print_prototype_summary(result):
    """Print a human-readable summary of the prototype results."""
    proto = result["prototype"]
    meta = result["metadata"]

    print()
    print(f"=== BEST COMBINATION (#{proto['best_combo_index'] + 1}) ===")
    print(f"Score: {meta['score']}  |  Placed: {meta['placed']}/{meta['total']}  |  Intersections: {meta['intersections']}")
    print()

    # Show selected words for multi-option entries
    multi = [sw for sw in proto["selected_words"] if len(sw["alternatives"]) > 1]
    if multi:
        print("Selected words:")
        for sw in multi:
            alts_str = " / ".join(sw["alternatives"])
            print(f"  {sw['chosen']:<16} (from: {alts_str})")
        print()

    # Show fixed words
    fixed = [sw["chosen"] for sw in proto["selected_words"] if len(sw["alternatives"]) == 1]
    if fixed:
        print(f"Fixed words: {', '.join(fixed)}")
        print()

    print(f"Evaluated: {proto['evaluated']}/{proto['total_combinations']} combinations"
          f" ({proto['skipped_duplicates']} skipped for duplicates)")
    print(f"Total time: {proto['total_runtime_ms'] / 1000:.1f}s")


def save_selected_csv(result, out_path):
    """Save the selected words and hints as a word,hint CSV for further editing."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for sw in result["prototype"]["selected_words"]:
            f.write(f"{sw['chosen']},{sw['hint']}\n")

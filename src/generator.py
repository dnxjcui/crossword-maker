import random
import time

ACROSS = "across"
DOWN = "down"


def generate_crossword(entries, rows, cols, seed=None, max_attempts=200):
    """Generate a crossword puzzle using best-of-N heuristic placement."""
    if seed is None:
        seed = random.randint(0, 2**31 - 1)

    rng = random.Random(seed)
    start = time.perf_counter()

    best = None
    best_score = -1
    best_attempt = 0

    for attempt in range(max_attempts):
        result = _run_attempt(entries, rows, cols, rng)
        score = _score_puzzle(result, len(entries))
        if score > best_score:
            best = result
            best_score = score
            best_attempt = attempt

    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    grid_cells = best["grid"]
    placed = best["placed"]
    total_intersections = sum(p["intersections"] for p in placed)

    return {
        "seed": seed,
        "grid": {
            "rows": rows,
            "cols": cols,
            "cells": grid_cells,
        },
        "placed": placed,
        "metadata": {
            "placed": len(placed),
            "total": len(entries),
            "best_attempt": best_attempt,
            "attempts": max_attempts,
            "intersections": total_intersections,
            "score": round(best_score, 4),
            "runtime_ms": elapsed_ms,
        },
    }


def _make_grid(rows, cols):
    return [["#"] * cols for _ in range(rows)]


def _run_attempt(entries, rows, cols, rng):
    order = list(entries)
    rng.shuffle(order)
    grid = _make_grid(rows, cols)
    placed = []

    for i, entry in enumerate(order):
        word = entry["word"]
        hint = entry["hint"]

        if len(word) > max(rows, cols):
            continue

        if i == 0:
            # Place first word across, centered
            if len(word) > cols:
                continue
            r = rows // 2
            c = (cols - len(word)) // 2
            _place_word(grid, word, r, c, ACROSS)
            placed.append({
                "word": word,
                "hint": hint,
                "row": r,
                "col": c,
                "direction": ACROSS,
                "intersections": 0,
            })
            continue

        # Find all valid candidate placements
        candidates = _find_candidates(grid, word, rows, cols)
        if not candidates:
            continue

        # Score and pick best
        best_cand = max(candidates, key=lambda c: _score_candidate(c, rows, cols))
        r, c, d, ints = best_cand
        _place_word(grid, word, r, c, d)
        placed.append({
            "word": word,
            "hint": hint,
            "row": r,
            "col": c,
            "direction": d,
            "intersections": ints,
        })

    return {"grid": grid, "placed": placed}


def _place_word(grid, word, row, col, direction):
    dr, dc = (0, 1) if direction == ACROSS else (1, 0)
    for i, ch in enumerate(word):
        grid[row + dr * i][col + dc * i] = ch


def _find_candidates(grid, word, rows, cols):
    candidates = []
    for direction in (ACROSS, DOWN):
        dr, dc = (0, 1) if direction == ACROSS else (1, 0)
        for idx, ch in enumerate(word):
            # Find all grid cells matching this letter
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] != ch:
                        continue
                    # Starting position if word[idx] lands on (r, c)
                    sr = r - dr * idx
                    sc = c - dc * idx
                    result = _validate_placement(grid, word, sr, sc, direction, rows, cols)
                    if result is not None:
                        candidates.append((sr, sc, direction, result))
    # Deduplicate
    seen = set()
    unique = []
    for cand in candidates:
        key = (cand[0], cand[1], cand[2])
        if key not in seen:
            seen.add(key)
            unique.append(cand)
    return unique


def _validate_placement(grid, word, row, col, direction, rows, cols):
    """Validate placement and return intersection count, or None if invalid."""
    dr, dc = (0, 1) if direction == ACROSS else (1, 0)
    length = len(word)

    # Rule 1: Bounds
    end_r = row + dr * (length - 1)
    end_c = col + dc * (length - 1)
    if row < 0 or col < 0 or end_r >= rows or end_c >= cols:
        return None

    # Rule 4: Bookend — cell before start must be '#' or OOB
    br, bc = row - dr, col - dc
    if 0 <= br < rows and 0 <= bc < cols and grid[br][bc] != "#":
        return None
    # Cell after end must be '#' or OOB
    ar, ac = row + dr * length, col + dc * length
    if 0 <= ar < rows and 0 <= ac < cols and grid[ar][ac] != "#":
        return None

    intersections = 0
    new_cells = 0
    # Perpendicular direction
    pr, pc = (1, 0) if direction == ACROSS else (0, 1)

    for i in range(length):
        r = row + dr * i
        c = col + dc * i
        cell = grid[r][c]

        if cell == "#":
            new_cells += 1
            # Rule 3: Parallel adjacency — perpendicular neighbors must be '#' or OOB
            for sign in (-1, 1):
                nr, nc = r + pr * sign, c + pc * sign
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
                    return None
        elif cell == word[i]:
            intersections += 1
        else:
            # Rule 2: Letter conflict
            return None

    # Rule 5: At least one new cell
    if new_cells == 0:
        return None

    return intersections


def _score_candidate(candidate, rows, cols):
    r, c, direction, intersections = candidate
    center_r, center_c = rows / 2, cols / 2
    dist = abs(r - center_r) + abs(c - center_c)
    max_dist = center_r + center_c
    centrality = 1.0 - dist / max_dist if max_dist > 0 else 1.0
    return 2.0 * intersections + 1.0 * centrality


def _score_puzzle(result, total_words):
    placed = result["placed"]
    grid = result["grid"]
    n_placed = len(placed)

    if total_words == 0:
        return 0.0

    placed_ratio = n_placed / total_words

    total_intersections = sum(p["intersections"] for p in placed)
    total_letters = sum(len(p["word"]) for p in placed)
    intersection_density = total_intersections / total_letters if total_letters > 0 else 0

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    filled = sum(1 for r in grid for c in r if c != "#")
    fill_density = filled / (rows * cols) if rows * cols > 0 else 0

    return 0.50 * placed_ratio + 0.30 * intersection_density + 0.20 * fill_density

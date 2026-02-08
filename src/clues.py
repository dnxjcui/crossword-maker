def extract_clues(puzzle):
    """Assign clue numbers and build across/down clue lists.

    Scans the grid left-to-right, top-to-bottom. A cell starts an across word
    if it's a letter preceded by '#'/edge and followed by a letter. Same logic
    vertically for down words. Sequential clue numbers are assigned.

    Modifies puzzle in place: removes 'placed', adds 'clues'.
    """
    grid = puzzle["grid"]["cells"]
    rows = puzzle["grid"]["rows"]
    cols = puzzle["grid"]["cols"]

    # Build lookup from placed words
    placement_lookup = {}
    for p in puzzle["placed"]:
        placement_lookup[(p["row"], p["col"], p["direction"])] = p

    across_clues = []
    down_clues = []
    clue_number = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                continue

            starts_across = False
            starts_down = False

            # Check across start: left is '#'/edge AND right is a letter
            left_blocked = (c == 0 or grid[r][c - 1] == "#")
            right_exists = (c + 1 < cols and grid[r][c + 1] != "#")
            if left_blocked and right_exists:
                starts_across = True

            # Check down start: above is '#'/edge AND below is a letter
            top_blocked = (r == 0 or grid[r - 1][c] == "#")
            bottom_exists = (r + 1 < rows and grid[r + 1][c] != "#")
            if top_blocked and bottom_exists:
                starts_down = True

            if not starts_across and not starts_down:
                continue

            clue_number += 1

            if starts_across:
                key = (r, c, "across")
                p = placement_lookup.get(key)
                if p:
                    across_clues.append({
                        "number": clue_number,
                        "answer": p["word"],
                        "hint": p["hint"],
                        "row": r,
                        "col": c,
                    })

            if starts_down:
                key = (r, c, "down")
                p = placement_lookup.get(key)
                if p:
                    down_clues.append({
                        "number": clue_number,
                        "answer": p["word"],
                        "hint": p["hint"],
                        "row": r,
                        "col": c,
                    })

    del puzzle["placed"]
    puzzle["clues"] = {
        "across": across_clues,
        "down": down_clues,
    }

    return puzzle

# Lightweight Crossword Generator (MVP)

Generate **one crossword at a time** from a rigid word+hint CSV, save it to `output/`, and view/iterate in a **lightweight GUI**.

## Requirements

* **Lightweight**: stdlib-only preferred (no heavy frameworks).
* **Fast**: typical inputs should generate in seconds.
* **Fast iteration**: GUI must support **Back / Forward / New Random** to browse layouts quickly.
* **Reproducible**: optional `--seed`.

## Repo Layout

```
ROOT/
  scripts/        # thin CLI entrypoints
  src/            # parsing, generation, scoring, serialization, GUI
  input/          # input CSV files
  output/         # generated crossword JSON files
```

## Input Format (Rigid CSV)

The input file is parsed **line-by-line**. Each non-empty line must be:

```
word,hint
```

Example `input/sample.csv`:

```
NEURON,A nerve cell
SYNAPSE,Junction between neurons
CORTEX,Outer brain layer
```

Rules:

* Exactly one comma separating `word` and `hint` (split on first comma).
* `word` is normalized to uppercase `A–Z` only (strip spaces/punctuation).
* Reject duplicates after normalization.

## Output Format

Write one file per crossword: `output/<name>.json`.

Minimum fields the GUI needs:

* `grid.cells` with `"#"` for blocks and letters for filled cells
* across/down clue lists with numbering and start coordinates
* generation metadata (seed, score, attempts)

Recommended schema:

```json
{
  "name": "sample",
  "seed": 123,
  "grid": {"rows": 15, "cols": 15, "cells": [["#","A"],["B","C"]]},
  "clues": {
    "across": [{"number": 1, "answer": "NEURON", "row": 3, "col": 5, "hint": "A nerve cell"}],
    "down":   [{"number": 2, "answer": "CORTEX", "row": 1, "col": 8, "hint": "Outer brain layer"}]
  },
  "metadata": {"placed": 23, "attempts": 142, "intersections": 31, "score": 0.87, "runtime_ms": 512}
}
```

## CLI (scripts/)

### Generate one crossword

```
python scripts/generate.py --input input/sample.csv --name sample --rows 15 --cols 15 --seed 123
```

* Generates **one** best puzzle within an attempt budget
* Writes `output/sample.json`
* Prints summary (placed, intersections, score, runtime)

### View a saved crossword

```
python scripts/view.py --puzzle output/sample.json
```

### GUI app (generate + iterate inside GUI)

```
python scripts/app.py --input input/sample.csv --rows 15 --cols 15
```

## GUI MVP (Required)

Use **tkinter** (preferred) or similarly lightweight option.

Must include:

* Grid renderer + Across/Down clue panes
* Metadata display (seed/score/placed)
* Buttons:

  * **Back**: previous layout in session history
  * **Forward**: next layout in history
  * **New Random**: generate a new layout immediately (append to history; truncate forward history)
  * Optional: **Save** current layout to `output/`

## Implementation Order (MVP)

1. `src/io.py`: parse rigid CSV, normalize words
2. `src/generator.py`: fast heuristic placement + attempt budget + scoring
3. `src/clues.py`: numbering + across/down clue extraction
4. `src/serialize.py`: save/load JSON
5. `src/gui.py`: viewer + history navigation

## Minimal src API

```python
def load_wordlist(path: str) -> list[dict]: ...

def generate_crossword(entries: list[dict], rows: int, cols: int, seed: int | None,
                       max_attempts: int = 200) -> dict: ...

def save_puzzle(puzzle: dict, out_path: str) -> None: ...
def load_puzzle(path: str) -> dict: ...

def run_viewer(puzzle: dict | None = None, *, input_path: str | None = None,
               rows: int = 15, cols: int = 15) -> None: ...
```

## MVP Done When

* `generate.py` produces valid `output/*.json` from `input/*.csv`.
* GUI can load JSON and can also generate in-app.
* GUI supports **Back / Forward / New Random**.
* Same seed produces identical output.

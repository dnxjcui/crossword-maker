import tkinter as tk
from tkinter import filedialog, messagebox

from src.io import load_wordlist
from src.generator import generate_crossword
from src.clues import extract_clues
from src.serialize import save_puzzle


CELL_SIZE = 36
NUMBER_FONT_SIZE = 8
LETTER_FONT_SIZE = 14


class CrosswordViewer:
    def __init__(self, root, puzzle=None, *, input_path=None, rows=15, cols=15):
        self.root = root
        self.input_path = input_path
        self.rows = rows
        self.cols = cols
        self.entries = None

        # History
        self.history = []
        self.history_index = -1

        # Load entries if in app mode
        if input_path:
            self.entries = load_wordlist(input_path)

        self.root.title("Crossword Generator")
        self._build_ui()

        if puzzle:
            self._push_puzzle(puzzle)
        elif self.entries:
            self._generate_new()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.btn_back = tk.Button(toolbar, text="< Back", command=self._go_back)
        self.btn_back.pack(side=tk.LEFT, padx=2)

        self.btn_forward = tk.Button(toolbar, text="Forward >", command=self._go_forward)
        self.btn_forward.pack(side=tk.LEFT, padx=2)

        self.btn_new = tk.Button(toolbar, text="New Random", command=self._generate_new)
        self.btn_new.pack(side=tk.LEFT, padx=10)

        self.btn_save = tk.Button(toolbar, text="Save", command=self._save_puzzle)
        self.btn_save.pack(side=tk.LEFT, padx=2)

        self.meta_label = tk.Label(toolbar, text="", anchor=tk.W)
        self.meta_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        # Main content area
        content = tk.Frame(self.root)
        content.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for grid (left side)
        canvas_width = self.cols * CELL_SIZE + 2
        canvas_height = self.rows * CELL_SIZE + 2
        self.canvas = tk.Canvas(content, width=canvas_width, height=canvas_height,
                                bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))

        # Clues panel (right side)
        clue_frame = tk.Frame(content)
        clue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Across clues
        tk.Label(clue_frame, text="ACROSS", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W)
        across_frame = tk.Frame(clue_frame)
        across_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.across_text = tk.Text(across_frame, wrap=tk.WORD, width=45, height=12,
                                   state=tk.DISABLED, cursor="arrow")
        across_scroll = tk.Scrollbar(across_frame, command=self.across_text.yview)
        self.across_text.configure(yscrollcommand=across_scroll.set)
        self.across_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        across_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Down clues
        tk.Label(clue_frame, text="DOWN", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W)
        down_frame = tk.Frame(clue_frame)
        down_frame.pack(fill=tk.BOTH, expand=True)
        self.down_text = tk.Text(down_frame, wrap=tk.WORD, width=45, height=12,
                                 state=tk.DISABLED, cursor="arrow")
        down_scroll = tk.Scrollbar(down_frame, command=self.down_text.yview)
        self.down_text.configure(yscrollcommand=down_scroll.set)
        self.down_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        down_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._update_buttons()

    def _push_puzzle(self, puzzle):
        # Truncate forward history (browser-style)
        self.history = self.history[:self.history_index + 1]
        self.history.append(puzzle)
        self.history_index = len(self.history) - 1
        self._display_puzzle(puzzle)
        self._update_buttons()

    def _display_puzzle(self, puzzle):
        self._draw_grid(puzzle)
        self._draw_clues(puzzle)
        self._update_meta(puzzle)

    def _draw_grid(self, puzzle):
        self.canvas.delete("all")
        cells = puzzle["grid"]["cells"]
        r_count = puzzle["grid"]["rows"]
        c_count = puzzle["grid"]["cols"]

        # Build number map from clues
        number_map = {}
        for clue in puzzle.get("clues", {}).get("across", []):
            number_map[(clue["row"], clue["col"])] = clue["number"]
        for clue in puzzle.get("clues", {}).get("down", []):
            pos = (clue["row"], clue["col"])
            if pos not in number_map:
                number_map[pos] = clue["number"]

        for r in range(r_count):
            for c in range(c_count):
                x1 = c * CELL_SIZE + 1
                y1 = r * CELL_SIZE + 1
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cell = cells[r][c]

                if cell == "#":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="black")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")
                    # Letter
                    self.canvas.create_text(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2 + 2,
                                            text=cell, font=("Courier", LETTER_FONT_SIZE, "bold"))
                    # Clue number
                    num = number_map.get((r, c))
                    if num is not None:
                        self.canvas.create_text(x1 + 4, y1 + 3, text=str(num),
                                                font=("TkDefaultFont", NUMBER_FONT_SIZE),
                                                anchor=tk.NW)

    def _draw_clues(self, puzzle):
        clues = puzzle.get("clues", {})

        self.across_text.configure(state=tk.NORMAL)
        self.across_text.delete("1.0", tk.END)
        for clue in clues.get("across", []):
            self.across_text.insert(tk.END, f"{clue['number']}. {clue['hint']}\n")
        self.across_text.configure(state=tk.DISABLED)

        self.down_text.configure(state=tk.NORMAL)
        self.down_text.delete("1.0", tk.END)
        for clue in clues.get("down", []):
            self.down_text.insert(tk.END, f"{clue['number']}. {clue['hint']}\n")
        self.down_text.configure(state=tk.DISABLED)

    def _update_meta(self, puzzle):
        meta = puzzle.get("metadata", {})
        seed = puzzle.get("seed", "?")
        placed = meta.get("placed", "?")
        total = meta.get("total", "?")
        score = meta.get("score", "?")
        ints = meta.get("intersections", "?")
        ms = meta.get("runtime_ms", "?")
        self.meta_label.config(
            text=f"Seed: {seed}  |  Placed: {placed}/{total}  |  "
                 f"Intersections: {ints}  |  Score: {score}  |  {ms}ms"
        )

    def _update_buttons(self):
        has_entries = self.entries is not None
        self.btn_back.config(state=tk.NORMAL if self.history_index > 0 else tk.DISABLED)
        self.btn_forward.config(
            state=tk.NORMAL if self.history_index < len(self.history) - 1 else tk.DISABLED
        )
        self.btn_new.config(state=tk.NORMAL if has_entries else tk.DISABLED)
        self.btn_save.config(state=tk.NORMAL if self.history else tk.DISABLED)

    def _go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._display_puzzle(self.history[self.history_index])
            self._update_buttons()

    def _go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._display_puzzle(self.history[self.history_index])
            self._update_buttons()

    def _generate_new(self):
        if not self.entries:
            return
        puzzle = generate_crossword(self.entries, self.rows, self.cols)
        puzzle = extract_clues(puzzle)
        self._push_puzzle(puzzle)

    def _save_puzzle(self):
        if not self.history:
            return
        puzzle = self.history[self.history_index]
        seed = puzzle.get("seed", "puzzle")
        path = filedialog.asksaveasfilename(
            initialdir="output",
            initialfile=f"crossword_{seed}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if path:
            save_puzzle(puzzle, path)
            messagebox.showinfo("Saved", f"Puzzle saved to {path}")


def run_viewer(puzzle=None, *, input_path=None, rows=15, cols=15):
    """Launch the crossword viewer GUI."""
    root = tk.Tk()
    CrosswordViewer(root, puzzle=puzzle, input_path=input_path, rows=rows, cols=cols)
    root.mainloop()

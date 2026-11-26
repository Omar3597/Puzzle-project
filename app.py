# app.py - GUI for the 8-Puzzle AI Solver (customtkinter + matplotlib)
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from puzzle import GOAL, parse_state, is_solvable, shuffle_state, moves_from_path
from algorithms import ALGORITHMS

ctk.set_appearance_mode("dark")

TILE_COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b",
               "#10b981", "#06b6d4", "#ef4444", "#84cc16"]  # one per tile 1..8
BLANK_COLOR = "#1f2937"
GOAL_COLOR = "#16a34a"
STUCK_COLOR = "#dc2626"
SEARCH_DELAY = 15   # ms between explored states (fast)
SOLVE_DELAY = 400   # ms between solution moves (slow)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AIM 315 - Intelligent Agent & Search Problem")
        self.geometry("1400x720")

        self.puzzle = (1, 2, 3, 4, 0, 6, 7, 5, 8)  # current puzzle (start state)
        self.results = {}                          # algorithm name -> result dict
        self.buttons = []                          # widgets to disable while animating

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0, minsize=370)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_board()
        self.build_charts()
        self.show_state(self.puzzle)
        self.draw_charts()

    # ---------- building the window ----------
    def build_sidebar(self):
        side = ctk.CTkFrame(self, width=280)
        side.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(side, text="8-Puzzle AI Solver",
                     font=("Arial", 22, "bold")).pack(padx=20, pady=(20, 15))

        ctk.CTkLabel(side, text="Custom state (0 = blank)").pack()
        self.entry = ctk.CTkEntry(side, width=220)
        self.entry.insert(0, "1,2,3,4,0,6,7,5,8")
        self.entry.pack(pady=5)
        set_button = ctk.CTkButton(side, text="Set State", command=self.on_set_state)
        set_button.pack(pady=5)

        shuffle_button = ctk.CTkButton(side, text="Shuffle", command=self.on_shuffle)
        shuffle_button.pack(pady=(15, 5))

        ctk.CTkLabel(side, text="Algorithm").pack(pady=(20, 0))
        self.menu = ctk.CTkOptionMenu(side, values=list(ALGORITHMS.keys()), width=220)
        self.menu.pack(pady=5)

        run_button = ctk.CTkButton(side, text="RUN SELECTED ALGORITHM",
                                   fg_color="#16a34a", hover_color="#15803d",
                                   command=self.on_run)
        run_button.pack(pady=15)

        self.status = ctk.CTkLabel(side, text="Ready", wraplength=240, justify="left")
        self.status.pack(padx=15, pady=10)

        self.buttons = [self.entry, set_button, shuffle_button, self.menu, run_button]

    def build_board(self):
        center = ctk.CTkFrame(self)
        center.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)

        self.board = ctk.CTkFrame(center, fg_color="transparent")
        self.board.grid(row=0, column=0)
        self.tiles = []  # 9 labels, one per board square
        for i in range(9):
            label = ctk.CTkLabel(self.board, text="", width=100, height=100,
                                 corner_radius=12, font=("Arial", 38, "bold"))
            label.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.tiles.append(label)

    def build_charts(self):
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(right, text="Performance Comparison",
                     font=("Arial", 18, "bold")).pack(pady=(10, 0))

        self.figure = Figure(figsize=(5, 5.5), facecolor="#2b2b2b")
        self.ax_time = self.figure.add_subplot(211)
        self.ax_nodes = self.figure.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # ---------- drawing ----------
    def show_state(self, state, color=None):
        """Draw a state on the board. 'color' (optional) paints every tile that colour."""
        for i, number in enumerate(state):
            if number == 0:
                self.tiles[i].configure(text="", fg_color=BLANK_COLOR)
            else:
                self.tiles[i].configure(text=str(number),
                                        fg_color=color or TILE_COLORS[number - 1])

    def draw_charts(self):
        names = list(self.results.keys())
        times = [self.results[n]["time"] for n in names]
        nodes = [self.results[n]["expanded_nodes"] for n in names]
        lengths = [len(self.results[n]["path"]) - 1 for n in names]
        short = [n.split(" ")[0] for n in names]  # "A*", "IDA*", "BFS", "Hill"

        for ax in (self.ax_time, self.ax_nodes):
            ax.clear()
            ax.set_facecolor("#2b2b2b")
            ax.tick_params(colors="white", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#888888")

        self.ax_time.set_title("Execution Time (s)", color="white", fontsize=11)
        self.ax_time.bar(short, times, color="#3b82f6")

        self.ax_nodes.set_title("Nodes vs Path Length", color="white", fontsize=11)
        positions = list(range(len(names)))
        self.ax_nodes.bar([p - 0.2 for p in positions], nodes, width=0.4,
                          color="orange", label="Expanded nodes")
        self.ax_nodes.bar([p + 0.2 for p in positions], lengths, width=0.4,
                          color="green", label="Path length")
        self.ax_nodes.set_xticks(positions)
        self.ax_nodes.set_xticklabels(short)
        self.ax_nodes.set_yscale("symlog")  # nodes are much bigger than path length
        if names:
            self.ax_nodes.legend(facecolor="#2b2b2b", labelcolor="white", fontsize=7, loc="upper right")

        self.figure.tight_layout()
        self.canvas.draw()

    # ---------- button actions ----------
    def new_puzzle(self, state):
        """Use a new puzzle: show it and clear the old results."""
        self.puzzle = state
        self.results = {}
        self.show_state(state)
        self.draw_charts()

    def on_set_state(self):
        try:
            state = parse_state(self.entry.get())
        except ValueError as error:
            self.status.configure(text="Invalid input: " + str(error))
            return
        if not is_solvable(state):
            self.status.configure(text="Unsolvable puzzle: the number of inversions is odd.")
            return
        self.new_puzzle(state)
        self.status.configure(text="State set. Choose an algorithm.")

    def on_shuffle(self):
        state = shuffle_state()
        self.entry.delete(0, "end")
        self.entry.insert(0, ",".join(str(n) for n in state))
        self.new_puzzle(state)
        self.status.configure(text="Shuffled. Choose an algorithm.")

    def set_buttons(self, enabled):
        for widget in self.buttons:
            widget.configure(state="normal" if enabled else "disabled")

    def on_run(self):
        name = self.menu.get()
        self.status.configure(text="Running " + name + "...")
        self.update_idletasks()
        result = ALGORITHMS[name](self.puzzle)  # time is measured inside the algorithm
        self.results[name] = result
        self.draw_charts()
        self.set_buttons(False)
        self.status.configure(text="Searching... (" + name + ")")
        self.animate_search(name, result, 0)

    # ---------- animation (uses after(), never sleep) ----------
    def animate_search(self, name, result, i):
        """Phase 1: show the explored states quickly."""
        explored = result["explored"]
        if i < len(explored):
            self.show_state(explored[i])
            self.after(SEARCH_DELAY, self.animate_search, name, result, i + 1)
        else:
            self.status.configure(text="Solving... (" + name + ")")
            self.show_state(result["path"][0])
            self.after(SOLVE_DELAY, self.animate_solution, name, result, 1)

    def animate_solution(self, name, result, i):
        """Phase 2: show the path one move at a time."""
        path = result["path"]
        if i < len(path):
            self.show_state(path[i])
            self.after(SOLVE_DELAY, self.animate_solution, name, result, i + 1)
        else:
            self.finish(name, result)

    def finish(self, name, result):
        path = result["path"]
        moves = moves_from_path(path)
        if result["solved"]:
            self.show_state(path[-1], GOAL_COLOR)  # whole board turns green
            text = ("Goal reached! (" + name + ")\nCost: " + str(len(moves)) +
                    "\nMoves: " + (", ".join(moves) if moves else "none"))
        else:
            self.show_state(path[-1], STUCK_COLOR)  # red = stuck
            text = ("Failed: " + result["message"] + " (" + name + ")" +
                    "\nMoves made: " + str(len(moves)) +
                    "\n" + (", ".join(moves) if moves else "no move was possible"))
        self.status.configure(text=text)
        self.set_buttons(True)


if __name__ == "__main__":
    App().mainloop()

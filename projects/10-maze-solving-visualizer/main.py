"""Compare real BFS and DFS exploration in synchronized Tk canvases."""

import argparse
from maze import PREDEFINED, bfs, dfs, generate_maze, parse_maze, text_solution


class MazeApp:
    def __init__(self, root, maze):
        import tkinter as tk
        from tkinter import ttk

        self.root = root
        root.title("Maze Lab - BFS and DFS")
        root.geometry("1120x700")
        body = ttk.Frame(root, padding=22)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Maze Lab", font=("Segoe UI", 25, "bold")).pack(anchor="w")
        ttk.Label(body, text="One maze. Two strategies. Watch the frontier become a path.").pack(anchor="w", pady=(0, 15))
        controls = ttk.Frame(body)
        controls.pack(fill="x")
        self.seed = tk.StringVar(value="17")
        self.delay = tk.IntVar(value=12)
        for label, command in (("Generate", self.generate), ("Predefined", lambda: self.load(parse_maze(PREDEFINED))),
                               ("Animate", self.animate), ("Pause / resume", self.pause), ("Step", self.step)):
            ttk.Button(controls, text=label, command=command).pack(side="left", padx=(0, 6))
        ttk.Label(controls, text="Seed").pack(side="left")
        ttk.Entry(controls, textvariable=self.seed, width=6).pack(side="left", padx=5)
        ttk.Label(controls, text="Delay (ms)").pack(side="left")
        tk.Scale(controls, from_=1, to=100, orient="horizontal", variable=self.delay, length=130).pack(side="left")
        boards = ttk.Frame(body)
        boards.pack(fill="both", expand=True, pady=18)
        self.canvases, self.labels = [], []
        for title in ("BFS - breadth first", "DFS - depth first"):
            panel = ttk.Frame(boards)
            panel.pack(side="left", fill="both", expand=True, padx=8)
            ttk.Label(panel, text=title, font=("Segoe UI", 15, "bold")).pack()
            canvas = tk.Canvas(panel, width=500, height=320, bg="#0f172a", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            label = ttk.Label(panel, text="")
            label.pack(pady=8)
            self.canvases.append(canvas)
            self.labels.append(label)
        self.status = ttk.Label(body, text="Teal / violet = explored. Gold = final path. Green = start. Red = exit.")
        self.status.pack(anchor="w")
        ttk.Label(body, text="BFS explores by distance, so its first route is shortest in an unweighted maze.\n"
                            "DFS follows a branch; try Predefined to see a longer first route.").pack(anchor="w", pady=8)
        self.timer = None
        self.running = False
        self.load(maze)
        root.bind("<Escape>", lambda _: root.destroy())

    def load(self, maze):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.running = False
        self.maze = maze
        self.results = [bfs(maze), dfs(maze)]
        self.index = 0
        self.draw()

    def generate(self):
        try:
            self.load(generate_maze(seed=int(self.seed.get())))
        except ValueError as exc:
            self.status.configure(text=str(exc))

    def draw(self):
        for number, (canvas, label, result) in enumerate(zip(self.canvases, self.labels, self.results)):
            canvas.delete("all")
            rows, columns = len(self.maze.rows), len(self.maze.rows[0])
            size = min(490 / columns, 310 / rows)
            explored = set(result.explored[:self.index])
            finished = self.index >= len(result.explored)
            path = set(result.path) if finished else set()
            for r, row in enumerate(self.maze.rows):
                for c, value in enumerate(row):
                    color = "#0f172a" if value == "#" else "#e2e8f0"
                    if (r, c) in explored:
                        color = "#14b8a6" if number == 0 else "#a78bfa"
                    if (r, c) in path:
                        color = "#fbbf24"
                    if (r, c) == self.maze.start:
                        color = "#22c55e"
                    elif (r, c) == self.maze.goal:
                        color = "#f43f5e"
                    canvas.create_rectangle(c * size, r * size, (c + 1) * size, (r + 1) * size,
                                            fill=color, outline="#334155", width=0.4)
            length = "not reached" if not finished else (str(result.path_length) if result.path else "no route")
            label.configure(text=f"Explored: {min(self.index, len(result.explored))} | Path: {length} edges")

    def step(self):
        self.index = min(self.index + 1, max(len(result.explored) for result in self.results))
        self.draw()

    def tick(self):
        self.timer = None
        if not self.running:
            return
        self.step()
        if self.index < max(len(result.explored) for result in self.results):
            self.timer = self.root.after(self.delay.get(), self.tick)
        else:
            self.running = False

    def animate(self):
        self.load(self.maze)
        self.running = True
        self.tick()

    def pause(self):
        self.running = not self.running
        if self.running and self.timer is None:
            self.tick()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predefined", action="store_true")
    parser.add_argument("--solve", action="store_true", help="Print solutions without opening a window")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--rows", type=int, default=21)
    parser.add_argument("--cols", type=int, default=31)
    args = parser.parse_args()
    try:
        maze = parse_maze(PREDEFINED) if args.predefined else generate_maze(args.rows, args.cols, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    if args.solve:
        for name, solve in (("BFS", bfs), ("DFS", dfs)):
            result = solve(maze)
            print(f"{name}: explored={len(result.explored)}, path={result.path_length} edges")
            print(text_solution(maze, result))
        return
    import tkinter as tk
    root = tk.Tk()
    MazeApp(root, maze)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Button-based desktop matches; python main.py still opens the CLI."""

import random
import tkinter as tk
from tkinter import ttk

from rps import CHOICES, Match


class RockPaperScissorsApp:
    def __init__(self, root: tk.Tk, rng: random.Random | None = None):
        self.root = root
        self.rng = rng or random.Random()
        root.title("Rock, Paper, Scissors")
        root.geometry("790x780")
        root.minsize(730, 750)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="white")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 27, "bold"))
        style.configure("Card.TLabel", background="white", foreground="#334155", font=("Segoe UI", 12))
        style.configure("Score.TLabel", background="white", foreground="#0f172a", font=("Segoe UI", 25, "bold"))
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#e2e8f0", foreground="#334155", font=("Segoe UI", 10, "bold"), padding=6)
        for name, color, active in (("rock", "#2563eb", "#1d4ed8"), ("paper", "#0f766e", "#115e59"),
                                    ("scissors", "#7c3aed", "#6d28d9")):
            style.configure(f"{name}.TButton", background=color, foreground="white",
                            font=("Segoe UI", 15, "bold"), padding=(18, 20), anchor="center")
            style.map(f"{name}.TButton", background=[("disabled", "#94a3b8"), ("active", active)])

        page = ttk.Frame(root, padding=26, style="Page.TFrame")
        page.pack(fill="both", expand=True)
        ttk.Label(page, text="02 / MAKE YOUR MOVE", style="Page.TLabel").pack(anchor="w")
        ttk.Label(page, text="Rock. Paper. Scissors.", style="Title.TLabel").pack(anchor="w", pady=(6, 5))
        ttk.Label(page, text="Pick a move. See the matchup. Build your score.", style="Page.TLabel").pack(anchor="w")
        settings = ttk.Frame(page, style="Page.TFrame")
        settings.pack(fill="x", pady=16)
        ttk.Label(settings, text="Rounds", style="Page.TLabel").pack(side="left", padx=(0, 10))
        self.rounds = tk.StringVar(value="5")
        selector = ttk.Combobox(settings, textvariable=self.rounds, values=("3", "5", "7"), state="readonly", width=5)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda _: self.new_match())
        ttk.Button(settings, text="New match", command=self.new_match, padding=8).pack(side="right")

        scores = ttk.Frame(page, style="Page.TFrame")
        scores.pack(fill="x")
        self.score_labels = {}
        for index, (key, title) in enumerate((("win", "Your wins"), ("loss", "Computer wins"), ("draw", "Draws"))):
            scores.columnconfigure(index, weight=1)
            card = ttk.Frame(scores, style="Card.TFrame", padding=(18, 12))
            card.grid(row=0, column=index, sticky="ew", padx=(0, 10 if index < 2 else 0))
            ttk.Label(card, text=title, style="Card.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="Score.TLabel")
            value.pack(anchor="w")
            self.score_labels[key] = value

        moves = ttk.Frame(page, style="Page.TFrame")
        moves.pack(fill="x", pady=18)
        self.move_buttons = []
        for column, choice in enumerate(CHOICES):
            moves.columnconfigure(column, weight=1)
            button = ttk.Button(moves, text=f"{choice.upper()}\n[{choice[0].upper()}]",
                                style=f"{choice}.TButton", command=lambda value=choice: self.choose(value))
            button.grid(row=0, column=column, sticky="ew", padx=(0, 10 if column < 2 else 0))
            self.move_buttons.append(button)
            root.bind(f"<Key-{choice[0]}>", lambda _, value=choice: self.choose(value))
            root.bind(f"<Key-{choice[0].upper()}>", lambda _, value=choice: self.choose(value))

        self.result_label = ttk.Label(page, text="", style="Page.TLabel", font=("Segoe UI", 14, "bold"), wraplength=700)
        self.result_label.pack(anchor="w")
        self.match_label = ttk.Label(page, style="Page.TLabel", wraplength=700)
        self.match_label.pack(anchor="w", pady=(6, 12))
        self.history = ttk.Treeview(page, columns=("round", "you", "computer", "result"), show="headings", height=5)
        for name, label, width in (("round", "Round", 65), ("you", "Your move", 180),
                                   ("computer", "Computer move", 180), ("result", "Outcome", 170)):
            self.history.heading(name, text=label)
            self.history.column(name, width=width, anchor="w")
        self.history.pack(fill="both", expand=True)
        ttk.Label(page, text="Keyboard: R / P / S. Draws count as rounds. Changing the round count resets the match.",
                  style="Page.TLabel", wraplength=700).pack(anchor="w", pady=(12, 0))
        self.new_match()

    def new_match(self) -> None:
        self.match = Match(int(self.rounds.get()))
        self.history.delete(*self.history.get_children())
        for label in self.score_labels.values():
            label.configure(text="0")
        for button in self.move_buttons:
            button.configure(state="normal")
        self.result_label.configure(text="Ready when you are. Choose your first move.", foreground="#334155")
        self.match_label.configure(text=f"Round 1 of {self.match.rounds}")

    def choose(self, player: str) -> None:
        if self.match.finished:
            return
        computer = self.rng.choice(CHOICES)
        result = self.match.play(player, computer)
        count = len(self.match.history)
        self.history.insert("", "end", values=(count, player.title(), computer.title(), result.upper()))
        self.history.see(self.history.get_children()[-1])
        for key, label in self.score_labels.items():
            label.configure(text=str(self.match.score[key]))
        explanation = {"win": f"You win! {player.title()} beats {computer}.",
                       "loss": f"Computer wins. {computer.title()} beats {player}.",
                       "draw": f"A draw - you both chose {player}."}[result]
        color = {"win": "#047857", "loss": "#be123c", "draw": "#6d28d9"}[result]
        self.result_label.configure(text=explanation, foreground=color)
        if self.match.finished:
            score = self.match.score
            outcome = ("You won the match!" if score["win"] > score["loss"] else
                       "The computer won this match." if score["loss"] > score["win"] else "The match is tied.")
            self.match_label.configure(text=f"{outcome} All {count} rounds played. Start a new match to play again.")
            for button in self.move_buttons:
                button.configure(state="disabled")
        else:
            self.match_label.configure(text=f"Next: round {count + 1} of {self.match.rounds}")


def main() -> None:
    root = tk.Tk()
    RockPaperScissorsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

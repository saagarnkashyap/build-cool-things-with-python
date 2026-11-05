"""Open the desktop game: python gui.py. The CLI remains in main.py."""

import random
import tkinter as tk
from tkinter import ttk

from guessing import GuessingRound, hint

DIFFICULTIES = {"Easy": (1, 20, 5), "Classic": (1, 100, 7), "Challenge": (1, 500, 8)}


class NumberGuessingApp:
    def __init__(self, root: tk.Tk, rng: random.Random | None = None):
        self.root = root
        self.rng = rng or random.Random()
        root.title("Number Guessing")
        root.geometry("740x760")
        root.minsize(680, 730)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="white")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 27, "bold"))
        style.configure("Card.TLabel", background="white", foreground="#334155", font=("Segoe UI", 12))
        style.configure("Primary.TButton", background="#2563eb", foreground="white", padding=(16, 11), font=("Segoe UI", 11, "bold"))
        style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("disabled", "#94a3b8")])
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#e2e8f0", foreground="#334155", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Attempts.Horizontal.TProgressbar", background="#2563eb", troughcolor="#dbeafe",
                        lightcolor="#2563eb", darkcolor="#2563eb", bordercolor="#dbeafe")

        page = ttk.Frame(root, padding=26, style="Page.TFrame")
        page.pack(fill="both", expand=True)
        ttk.Label(page, text="01 / PLAY WITH LOGIC", style="Page.TLabel").pack(anchor="w")
        ttk.Label(page, text="Find the hidden number.", style="Title.TLabel").pack(anchor="w", pady=(6, 5))
        ttk.Label(page, text="Use each hint to narrow your next guess.", style="Page.TLabel").pack(anchor="w")
        settings = ttk.Frame(page, style="Page.TFrame")
        settings.pack(fill="x", pady=18)
        ttk.Label(settings, text="Difficulty", style="Page.TLabel").pack(side="left", padx=(0, 10))
        self.difficulty = tk.StringVar(value="Classic")
        selector = ttk.Combobox(settings, textvariable=self.difficulty, values=list(DIFFICULTIES), state="readonly", width=14)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda _: self.new_game())
        ttk.Button(settings, text="New game", command=self.new_game, padding=8).pack(side="right")

        card = ttk.Frame(page, padding=20, style="Card.TFrame")
        card.pack(fill="x")
        self.range_label = ttk.Label(card, style="Card.TLabel")
        self.range_label.pack(anchor="w")
        entry_row = ttk.Frame(card, style="Card.TFrame")
        entry_row.pack(fill="x", pady=14)
        self.guess = tk.StringVar()
        self.entry = ttk.Entry(entry_row, textvariable=self.guess, font=("Segoe UI", 22), width=12)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.guess_button = ttk.Button(entry_row, text="Check guess", command=self.submit, style="Primary.TButton")
        self.guess_button.pack(side="left")
        self.feedback = ttk.Label(card, text="", style="Card.TLabel", wraplength=590)
        self.feedback.pack(anchor="w", pady=(0, 12))
        self.progress = ttk.Progressbar(card, mode="determinate", style="Attempts.Horizontal.TProgressbar")
        self.progress.pack(fill="x")
        self.attempts_label = ttk.Label(card, style="Card.TLabel")
        self.attempts_label.pack(anchor="w", pady=(8, 0))

        ttk.Label(page, text="Your guesses", style="Page.TLabel").pack(anchor="w", pady=(20, 8))
        self.history = ttk.Treeview(page, columns=("turn", "guess", "hint"), show="headings", height=5)
        for name, title, width in (("turn", "Turn", 60), ("guess", "Guess", 100), ("hint", "Hint", 400)):
            self.history.heading(name, text=title)
            self.history.column(name, width=width, anchor="w")
        self.history.pack(fill="both", expand=True)
        ttk.Label(page, text="Press Enter to guess. Changing difficulty starts a fresh round.", style="Page.TLabel").pack(anchor="w", pady=(12, 0))
        root.bind("<Return>", lambda _: self.submit())
        self.new_game()

    def new_game(self) -> None:
        low, high, limit = DIFFICULTIES[self.difficulty.get()]
        self.game = GuessingRound(low, high, limit, self.rng.randint(low, high))
        self.history.delete(*self.history.get_children())
        self.guess.set("")
        self.range_label.configure(text=f"Pick a number from {low} to {high}.")
        self.feedback.configure(text="A fresh secret is ready. What is your first guess?", foreground="#334155")
        self.entry.configure(state="normal")
        self.guess_button.configure(state="normal")
        self.update_attempts()
        self.entry.focus_set()

    def update_attempts(self) -> None:
        self.progress.configure(maximum=self.game.limit, value=self.game.remaining)
        self.attempts_label.configure(text=f"{self.game.remaining} of {self.game.limit} attempts left")

    def submit(self) -> None:
        if self.game.finished:
            return
        try:
            feedback = self.game.submit(self.guess.get())
        except ValueError as exc:
            self.feedback.configure(text=str(exc), foreground="#b45309")
            return
        guess = self.game.guesses[-1]
        self.history.insert("", "end", values=(len(self.game.guesses), guess, hint(guess, self.game.secret)))
        if self.game.won:
            feedback = f"You found it! {guess} was correct in {len(self.game.guesses)} attempt(s)."
        color = "#047857" if self.game.won else "#be123c" if self.game.finished else "#1d4ed8"
        self.feedback.configure(text=feedback, foreground=color)
        self.guess.set("")
        self.update_attempts()
        if self.game.finished:
            self.entry.configure(state="disabled")
            self.guess_button.configure(state="disabled")
        else:
            self.entry.focus_set()


def main() -> None:
    root = tk.Tk()
    NumberGuessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

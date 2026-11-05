"""A local desktop generator. The terminal version remains in main.py."""

import tkinter as tk
from tkinter import ttk

from passwords import DEFAULT_GROUPS, generate_passwords


class PasswordGeneratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.passwords: list[str] = []
        root.title("Password Generator")
        root.geometry("800x840")
        root.minsize(740, 810)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="white")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 27, "bold"))
        style.configure("Card.TLabel", background="white", foreground="#334155", font=("Segoe UI", 12))
        style.configure("Card.TCheckbutton", background="white", foreground="#334155", font=("Segoe UI", 11), padding=4)
        style.configure("Page.TCheckbutton", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Primary.TButton", background="#0f766e", foreground="white", padding=(18, 12), font=("Segoe UI", 11, "bold"))
        style.map("Primary.TButton", background=[("active", "#115e59"), ("disabled", "#94a3b8")])
        style.configure("Treeview", rowheight=34, font=("Consolas", 12))
        style.configure("Treeview.Heading", background="#e2e8f0", foreground="#334155", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#0f172a")])

        page = ttk.Frame(root, padding=26, style="Page.TFrame")
        page.pack(fill="both", expand=True)
        ttk.Label(page, text="03 / CREATE SOMETHING UNPREDICTABLE", style="Page.TLabel").pack(anchor="w")
        ttk.Label(page, text="Your next password.", style="Title.TLabel").pack(anchor="w", pady=(6, 5))
        ttk.Label(page, text="Generated locally with secure randomness. No account needed.", style="Page.TLabel").pack(anchor="w")

        settings = ttk.Frame(page, style="Card.TFrame", padding=20)
        settings.pack(fill="x", pady=20)
        self.length = tk.StringVar(value="16")
        self.count = tk.StringVar(value="1")
        sizes = ttk.Frame(settings, style="Card.TFrame")
        sizes.pack(fill="x")
        for column, (label, variable, low, high) in enumerate((("Characters per password", self.length, 4, 128),
                                                             ("Number of passwords", self.count, 1, 20))):
            group = ttk.Frame(sizes, style="Card.TFrame")
            group.pack(side="left", padx=(0, 36))
            ttk.Label(group, text=label, style="Card.TLabel").pack(anchor="w")
            ttk.Spinbox(group, from_=low, to=high, textvariable=variable, width=12,
                        font=("Segoe UI", 15)).pack(anchor="w", pady=(8, 0))
        ttk.Label(settings, text="Include at least one character from each selected group:",
                  style="Card.TLabel").pack(anchor="w", pady=(20, 8))
        checks = ttk.Frame(settings, style="Card.TFrame")
        checks.pack(fill="x")
        self.groups = []
        for label in ("Lowercase", "Uppercase", "Numbers", "Symbols"):
            selected = tk.BooleanVar(value=True)
            self.groups.append(selected)
            ttk.Checkbutton(checks, text=label, variable=selected, style="Card.TCheckbutton").pack(side="left", padx=(0, 12))
        ttk.Button(settings, text="Generate passwords", command=self.generate,
                   style="Primary.TButton").pack(anchor="w", pady=(18, 0))

        result_header = ttk.Frame(page, style="Page.TFrame")
        result_header.pack(fill="x")
        self.generated_label = ttk.Label(result_header, text="No passwords yet", style="Page.TLabel")
        self.generated_label.pack(side="left")
        self.show_passwords = tk.BooleanVar(value=False)
        ttk.Checkbutton(result_header, text="Show passwords", variable=self.show_passwords,
                        command=self.update_visibility, style="Page.TCheckbutton").pack(side="right")
        result_area = ttk.Frame(page)
        result_area.pack(fill="both", expand=True, pady=(10, 0))
        result_area.rowconfigure(0, weight=1)
        result_area.columnconfigure(0, weight=1)
        self.table = ttk.Treeview(result_area, columns=("number", "password"), show="headings", height=4, selectmode="browse")
        self.table.heading("number", text="#")
        self.table.heading("password", text="Generated password")
        self.table.column("number", width=50, stretch=False)
        self.table.column("password", width=630, minwidth=630, stretch=False)
        vertical = ttk.Scrollbar(result_area, orient="vertical", command=self.table.yview)
        horizontal = ttk.Scrollbar(result_area, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(page, style="Page.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        self.copy_button = ttk.Button(actions, text="Copy selected", command=self.copy_selected, padding=8, state="disabled")
        self.copy_button.pack(side="left")
        ttk.Button(actions, text="Clear results", command=self.clear_results, padding=8).pack(side="left", padx=10)
        self.status = ttk.Label(page, text="Choose your settings, then Generate.", style="Page.TLabel", wraplength=730)
        self.status.pack(anchor="w", pady=(12, 0))
        ttk.Label(page, text="Nothing is saved. Clipboard contents remain until replaced. Use long, unique passwords.",
                  style="Page.TLabel", wraplength=730).pack(anchor="w", pady=(8, 0))
        for variable in (self.length, self.count, *self.groups):
            variable.trace_add("write", self.settings_changed)

    def settings_changed(self, *_args) -> None:
        self.clear_results()
        self.status.configure(text="Settings changed. Generate a fresh batch to use these settings.", foreground="#334155")

    def clear_results(self) -> None:
        self.passwords = []
        self.table.delete(*self.table.get_children())
        self.copy_button.configure(state="disabled")
        self.generated_label.configure(text="No passwords yet")
        self.status.configure(text="Results cleared. Nothing has been saved.", foreground="#334155")

    def generate(self) -> None:
        self.clear_results()
        try:
            length, count = int(self.length.get()), int(self.count.get())
        except ValueError:
            self.status.configure(text="Enter whole numbers for length and count.", foreground="#b45309")
            return
        groups = tuple(group for group, selected in zip(DEFAULT_GROUPS, self.groups) if selected.get())
        try:
            self.passwords = generate_passwords(length, count, groups)
        except ValueError as exc:
            self.status.configure(text=str(exc), foreground="#b45309")
            return
        self.table.column("password", width=max(630, length * 11))
        self.update_visibility()
        self.table.selection_set("0")
        self.copy_button.configure(state="normal")
        self.generated_label.configure(text=f"{count} password(s) / {length} characters each")
        self.status.configure(text="Ready. Select a row to copy, or reveal the text with Show passwords.", foreground="#047857")

    def update_visibility(self) -> None:
        selected = self.table.selection()
        self.table.delete(*self.table.get_children())
        for index, password in enumerate(self.passwords):
            displayed = password if self.show_passwords.get() else "*" * len(password)
            self.table.insert("", "end", iid=str(index), values=(index + 1, displayed))
        if selected and self.table.exists(selected[0]):
            self.table.selection_set(selected[0])

    def copy_selected(self) -> None:
        selected = self.table.selection()
        if not selected or not self.passwords:
            self.status.configure(text="Generate a batch and select one row first.", foreground="#b45309")
            return
        try:
            password = self.passwords[int(selected[0])]
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
        except tk.TclError:
            self.status.configure(text="Clipboard unavailable on this system. Your password remains in this window.", foreground="#b45309")
            return
        self.status.configure(text="Copied the selected password. Replace the clipboard contents when finished.", foreground="#047857")


def main() -> None:
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

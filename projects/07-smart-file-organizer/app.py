"""A guided desktop preview with safe organization and manifest-based undo."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from organizer import apply_moves, plan_moves, safe_path, undo_moves


class OrganizerApp:
    def __init__(self, root):
        self.root = root
        self.plan = []
        self.preview_root = None
        self.last_manifest = None
        self.mode = "organize"
        root.title("Smart File Organizer")
        root.geometry("970x780")
        root.minsize(900, 750)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 26, "bold"))
        style.configure("Primary.TButton", background="#2563eb", foreground="white", padding=(18, 12), font=("Segoe UI", 11, "bold"))
        style.map("Primary.TButton", background=[("disabled", "#94a3b8"), ("active", "#1d4ed8")])
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#e2e8f0", foreground="#334155", font=("Segoe UI", 10, "bold"), padding=6)
        body = ttk.Frame(root, padding=26, style="Page.TFrame")
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="07 / A PLACE FOR EVERY FILE", style="Page.TLabel").pack(anchor="w")
        ttk.Label(body, text="Smart File Organizer", style="Title.TLabel").pack(anchor="w", pady=(6, 8))
        ttk.Label(body, text="1. Choose a folder   2. Review the preview   3. Organize when ready", style="Page.TLabel").pack(anchor="w")
        selector = ttk.Frame(body, style="Page.TFrame")
        selector.pack(fill="x", pady=(22, 12))
        self.folder = tk.StringVar()
        ttk.Entry(selector, textvariable=self.folder, state="readonly", font=("Segoe UI", 11)).pack(side="left", fill="x", expand=True, ipady=8)
        ttk.Button(selector, text="Choose folder...", command=self.choose, padding=10).pack(side="left", padx=(12, 0))
        self.summary = ttk.Label(body, text="Choose a folder to see where each file would go.", style="Page.TLabel")
        self.summary.pack(anchor="w", pady=(0, 10))
        table_area = ttk.Frame(body)
        table_area.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_area, columns=("source", "destination"), show="headings", height=7)
        self.table.heading("source", text="File now")
        self.table.heading("destination", text="After organizing")
        self.table.column("source", width=350)
        self.table.column("destination", width=490)
        scrollbar = ttk.Scrollbar(table_area, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        buttons = ttk.Frame(body, style="Page.TFrame")
        buttons.pack(fill="x", pady=18)
        ttk.Button(buttons, text="Refresh preview", command=self.preview, padding=10).pack(side="left")
        self.apply_button = ttk.Button(buttons, text="Organize files", command=self.apply, state="disabled", style="Primary.TButton")
        self.apply_button.pack(side="left", padx=12)
        self.undo_button = ttk.Button(buttons, text="Undo latest run", command=self.preview_undo, state="disabled", padding=10)
        self.undo_button.pack(side="right")
        self.status = ttk.Label(body, text="No files have been moved.", style="Page.TLabel", wraplength=890)
        self.status.pack(anchor="w")
        ttk.Label(body, text="Files move only after you review the table and click Organize. Recovery is saved automatically.",
                  style="Page.TLabel", wraplength=890).pack(anchor="w", pady=(12, 0))
        self.folder.trace_add("write", self.folder_changed)

    def folder_changed(self, *_):
        self.plan = []
        self.last_manifest = None
        self.preview_root = None
        self.mode = "organize"
        self.table.delete(*self.table.get_children())
        self.apply_button.configure(state="disabled", text="Organize files")
        self.undo_button.configure(state="disabled")
        self.summary.configure(text="Preview this folder before organizing.")
        self.status.configure(text="No changes made to the selected folder.")

    def choose(self):
        folder = filedialog.askdirectory(parent=self.root, title="Choose the folder to organize")
        if folder:
            self.folder.set(folder)
            self.preview()

    def refresh_undo(self):
        self.undo_button.configure(state="disabled")
        self.last_manifest = None
        try:
            state = safe_path(self.preview_root.resolve(), ".organizer/manifests")
            manifests = [path for path in state.glob("*.json") if path.is_file() and not path.is_symlink()]
            if manifests:
                self.last_manifest = max(manifests, key=lambda path: path.stat().st_mtime_ns)
                self.undo_button.configure(state="normal")
        except (OSError, ValueError):
            # The actual organize/undo functions will explain any unsafe state.
            pass

    def show_plan(self, plan, *, reverse=False):
        self.table.delete(*self.table.get_children())
        for entry in plan:
            source, destination = entry["source"], entry["destination"]
            self.table.insert("", "end", values=(destination, source) if reverse else (source, destination))
        self.table.heading("destination", text="After restoring" if reverse else "After organizing")

    def preview(self):
        self.apply_button.configure(state="disabled", text="Organize files")
        self.mode = "organize"
        try:
            if not self.folder.get().strip():
                raise ValueError("Choose a folder first.")
            self.preview_root = Path(self.folder.get())
            self.plan = plan_moves(self.preview_root)
            self.show_plan(self.plan)
            self.summary.configure(text=f"{len(self.plan)} file(s) ready to organize")
            self.status.configure(text=f"DRY RUN: {len(self.plan)} file(s). Nothing moved. Review the table, then click Organize files.")
            self.refresh_undo()
            if self.plan:
                self.apply_button.configure(state="normal")
        except (OSError, ValueError) as exc:
            self.status.configure(text=f"Could not preview: {exc}")

    def preview_undo(self):
        self.apply_button.configure(state="disabled")
        if self.last_manifest is None:
            self.status.configure(text="There is no saved run to undo for this folder.")
            return
        try:
            self.plan = undo_moves(self.last_manifest)
            self.mode = "undo"
            self.show_plan(self.plan, reverse=True)
            self.summary.configure(text=f"Undo preview: {len(self.plan)} file(s) to restore")
            self.status.configure(text="Review the original names above, then click Restore files. Changed files are protected.")
            self.apply_button.configure(text="Restore files", state="normal" if self.plan else "disabled")
            if not self.plan:
                self.status.configure(text="The latest run has no files left to restore.")
                self.undo_button.configure(state="disabled")
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            self.status.configure(text=f"Could not prepare undo: {exc}")

    def apply(self):
        self.apply_button.configure(state="disabled")
        if not self.plan or self.preview_root is None:
            self.status.configure(text="Choose a folder and review a preview first.")
            return
        try:
            if self.mode == "undo":
                restored = undo_moves(self.last_manifest, apply=True)
                self.summary.configure(text=f"Restored {len(restored)} file(s) to their original names")
                self.status.configure(text="Undo complete. Refresh the preview to see the folder again.")
                self.undo_button.configure(state="disabled")
            else:
                self.last_manifest, errors = apply_moves(self.preview_root, self.plan)
                self.undo_button.configure(state="normal")
                self.summary.configure(text="Organization complete" if not errors else "Finished with some files left in place")
                self.status.configure(text=("Some files need attention: " + "; ".join(errors)) if errors else
                                      f"Organized {len(self.plan)} file(s). Use Undo latest run if you want to restore them.")
            self.plan = []
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.status.configure(text=f"Stopped safely: {exc}")

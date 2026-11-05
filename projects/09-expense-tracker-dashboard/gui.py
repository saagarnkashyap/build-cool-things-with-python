"""Open the dashboard automatically, with a visible Start/Stop controller."""

import time
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

from launcher import DashboardServer


class ExpenseTrackerLauncher:
    def __init__(self, root, *, server=None, browser=None, autostart=True):
        self.root = root
        self.server = server or DashboardServer()
        self.browser = browser or (lambda url: webbrowser.open(url, new=2))
        self.timer = None
        self.details = ""
        root.title("Expense Tracker")
        root.geometry("680x430")
        root.minsize(640, 410)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 26, "bold"))
        style.configure("Primary.TButton", background="#0f766e", foreground="white", font=("Segoe UI", 11, "bold"), padding=(16, 12))
        style.map("Primary.TButton", background=[("active", "#115e59"), ("disabled", "#94a3b8")])
        body = ttk.Frame(root, padding=28, style="Page.TFrame")
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="09 / MAKE SENSE OF YOUR SPENDING", style="Page.TLabel").pack(anchor="w")
        ttk.Label(body, text="Expense Tracker", style="Title.TLabel").pack(anchor="w", pady=(6, 12))
        ttk.Label(body, text="Your dashboard opens in your browser. Start with sample data or choose your CSV.",
                  style="Page.TLabel", wraplength=610).pack(anchor="w")
        self.status = ttk.Label(body, text="Ready to start.", style="Page.TLabel", wraplength=610)
        self.status.pack(anchor="w", pady=(24, 12))
        self.link = tk.StringVar()
        ttk.Entry(body, textvariable=self.link, state="readonly", font=("Segoe UI", 11)).pack(fill="x", ipady=5)
        actions = ttk.Frame(body, style="Page.TFrame")
        actions.pack(fill="x", pady=20)
        self.start_button = ttk.Button(actions, text="Start dashboard", command=self.start, padding=12)
        self.start_button.pack(side="left")
        self.open_button = ttk.Button(actions, text="Open dashboard", command=self.open_browser, style="Primary.TButton", state="disabled")
        self.open_button.pack(side="left", padx=10)
        self.stop_button = ttk.Button(actions, text="Stop", command=self.stop, padding=12, state="disabled")
        self.stop_button.pack(side="left")
        ttk.Button(actions, text="Setup help", command=self.help, padding=12).pack(side="right")
        ttk.Label(body, text="Keep this window open while using the dashboard. Closing it stops the local server.",
                  style="Page.TLabel", wraplength=610).pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.close)
        if autostart:
            self.timer = root.after(150, self.start)

    def cancel_timer(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def start(self):
        self.cancel_timer()
        try:
            self.server.start()
        except OSError as exc:
            self.details = str(exc)
            self.status.configure(text="Could not start the dashboard. Open Setup help for the next steps.", foreground="#b45309")
            return
        self.start_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.configure(text="Starting your dashboard... it will open automatically.", foreground="#334155")
        self.link.set("")
        self.deadline = time.monotonic() + 45
        self.timer = self.root.after(200, self.poll_start)

    def poll_start(self):
        self.timer = None
        if self.server.healthy():
            self.link.set(self.server.url)
            self.open_button.configure(state="normal")
            self.status.configure(text="Your dashboard is ready. Choose your data in the browser.", foreground="#047857")
            self.open_browser()
            self.timer = self.root.after(1000, self.monitor)
            return
        process = self.server.process
        if process is None or process.poll() is not None or time.monotonic() >= self.deadline:
            self.details = self.server.diagnostics()
            self.server.stop()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status.configure(text="The dashboard could not start. Setup help has the details; then try Start again.", foreground="#b45309")
            return
        self.timer = self.root.after(200, self.poll_start)

    def monitor(self):
        self.timer = None
        if self.server.process is None or self.server.process.poll() is not None:
            self.details = self.server.diagnostics()
            self.stop()
            self.status.configure(text="The dashboard stopped. Click Start dashboard to reopen it.", foreground="#b45309")
            return
        self.timer = self.root.after(1000, self.monitor)

    def open_browser(self):
        if self.server.url:
            if not self.browser(self.server.url):
                self.status.configure(text="Copy the address above into your browser, or try Open dashboard again.", foreground="#b45309")

    def stop(self):
        self.cancel_timer()
        self.server.stop()
        self.link.set("")
        self.start_button.configure(state="normal")
        self.open_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.status.configure(text="Stopped. Click Start dashboard to open it again.", foreground="#334155")

    def help(self):
        message = ("The launcher uses the repository's .venv when available.\n\n"
                   "For first-time setup, install this project's requirements.txt as described in README.md. "
                   "Then open desktop.pyw or gui.py again.\n\n"
                   "A browser and a local desktop display are needed.")
        if self.details:
            message += "\n\nStartup details:\n" + self.details
        messagebox.showinfo("Expense Tracker setup", message, parent=self.root)

    def close(self):
        self.cancel_timer()
        self.server.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    ExpenseTrackerLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Open the organizer window without command-line flags."""

import tkinter as tk
from app import OrganizerApp


def main() -> None:
    root = tk.Tk()
    OrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Open QR Studio, preferring this repository's installed environment."""

import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    environment = Path(__file__).resolve().parents[2] / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if python.is_file() and Path(sys.prefix).resolve() != environment.resolve():
        subprocess.Popen([str(python), str(Path(__file__).resolve())],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    try:
        from qr_studio import Studio
    except ImportError:
        messagebox.showerror("QR Studio setup", "Install this project's requirements.txt in your Python environment, then open this launcher again.", parent=root)
        root.destroy()
        return
    root.deiconify()
    Studio(root)
    root.mainloop()


if __name__ == "__main__":
    main()

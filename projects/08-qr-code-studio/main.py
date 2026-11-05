import argparse
from pathlib import Path
from qr_studio import Studio, export_qr


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a QR image locally, or open the desktop studio.")
    parser.add_argument("text", nargs="?")
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("outputs/code.png"))
    parser.add_argument("--size", type=int, default=10, help="Pixels per module, 2-30")
    parser.add_argument("--foreground", default="#172554")
    parser.add_argument("--background", default="white")
    args = parser.parse_args()
    if args.gui or args.text is None:
        import tkinter as tk
        root = tk.Tk()
        Studio(root)
        root.mainloop()
        return
    try:
        print("Saved:", export_qr(args.text, args.output, scale=args.size,
                                  foreground=args.foreground, background=args.background))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"QR generation stopped: {exc}\n")


if __name__ == "__main__":
    main()

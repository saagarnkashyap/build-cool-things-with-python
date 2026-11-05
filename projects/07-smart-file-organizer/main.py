"""Preview by default. Use --apply only after reviewing the planned moves."""

import argparse
from pathlib import Path
from organizer import apply_moves, plan_moves, undo_moves


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path)
    parser.add_argument("--gui", action="store_true", help="Open the desktop preview")
    parser.add_argument("--apply", action="store_true", help="Perform the displayed moves")
    parser.add_argument("--undo", type=Path, metavar="MANIFEST", help="Preview or apply an undo")
    args = parser.parse_args()
    if args.gui:
        import tkinter as tk
        from app import OrganizerApp
        root = tk.Tk()
        OrganizerApp(root)
        root.mainloop()
        return
    if (args.folder is None) == (args.undo is None):
        parser.error("Choose a folder OR --undo MANIFEST.")
    try:
        plan = undo_moves(args.undo) if args.undo else plan_moves(args.folder)
        print("UNDO" if args.undo else "ORGANIZE", "| APPLY" if args.apply else "| DRY RUN (no changes)")
        for entry in plan:
            left, right = entry["source"], entry["destination"]
            print(f"  {right if args.undo else left} -> {left if args.undo else right}")
        print(f"{len(plan)} file(s).")
        if args.apply and args.undo:
            undo_moves(args.undo, apply=True)
        if args.apply and not args.undo:
            manifest, errors = apply_moves(args.folder, plan)
            print("Undo manifest:", manifest)
            if errors:
                parser.exit(1, "\n".join(errors) + "\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Organizer stopped: {exc}\n")


if __name__ == "__main__":
    main()

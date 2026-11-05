# Smart File Organizer

Preview extension-based categorization, deliberately apply the moves, and restore unchanged files with a durable undo manifest.

## Learning objectives

- Use pathlib for paths and shutil for streaming file transfers.
- Handle collisions, partial failures, symlinks, and changed files safely.
- Journal state before operations and validate recovery information.

## Installation

Only Python 3.12+ standard-library modules are required. The optional desktop interface uses Tk, included with many Python installations.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/07-smart-file-organizer`. Activate your Python environment first.

## Open the desktop app

Double-click `desktop.pyw` on Windows (with Python file associations configured),
or run `python gui.py` from this project folder. The terminal commands below
remain available in `main.py`.

1. Click **Choose folder**. A preview appears automatically; nothing moves yet.
2. Review the names, then click **Organize files**.
3. To reverse the latest run, click **Undo latest run**, review the restoration
   preview, then click **Restore files**.

The undo button finds the latest saved run in the chosen folder, including after
reopening the app. No manifest path needs to be typed. Existing and edited files
remain protected. **Refresh preview** returns to the organization view. Large
files may take time to hash and copy; keep the window open until it finishes.

[Organizer window](screenshots/app.png) / [undo preview](screenshots/undo.png).

## Usage

```powershell
python main.py "path/to/practice-folder"
python main.py "path/to/practice-folder" --apply
python main.py --undo "path/to/practice-folder/.organizer/manifests/ID.json"
python main.py --undo "path/to/practice-folder/.organizer/manifests/ID.json" --apply
python main.py --gui
```

The default is a dry run. Only regular, non-hidden files directly inside the selected directory are considered; subfolders and symlinks are left alone. Categories include Images, Documents, Audio, Video, Archives, Code, and Other. Duplicates receive suffixes such as `note (2).txt`. Transfers create the destination exclusively, copy with shutil, verify both SHA-256 hashes, and then remove the old directory entry to complete the move. Existing destinations are never overwritten. No user file is discarded, and no directory is automatically cleaned up.

Manifests live inside `.organizer/manifests/`. Undo also previews by default and refuses to overwrite a newly created source or restore edited content. A pending journal entry can be recovered after interruption. The desktop Organize files button is enabled only after preview.

## Tests and representative output

```powershell
python -m unittest discover -s tests -v
```

[Application capture](screenshots/app.png). See [samples](samples/) for outputs from real execution and
[exercises](exercises.md) for follow-up challenges. The repository-wide test
command is `python scripts/run_project_tests.py` from the repository root.

## Troubleshooting

Practice on a temporary folder first. Close programs that are writing into the folder: filesystem writers outside this tool do not share its lock. A copy error retains the original and any partial destination for manual inspection. Resolve the reported conflict and preview again. An interrupted process can leave `.organizer/active.lock`; confirm no organizer is running before manually removing only that lock. Keep the original manifest in place and never edit it to force an undo.


To exercise the click-through flows and regenerate the real captures, run
`python scripts/check_tool_guis.py` from the repository root. This optional
verification command uses the capture dependencies in
`scripts/requirements-verification.txt`; it stops its temporary local server.

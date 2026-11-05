# QR Code Studio

Create QR codes locally from text or HTTP(S) URLs, preview them in a desktop studio, and export PNG or scalable SVG.

## Learning objectives

- Validate text, URLs, sizes, and color contrast.
- Reuse one QR matrix across raster and vector formats.
- Preserve the quiet zone and verify decoded content before sharing.

## Installation

Install `qrcode[pil]` (QR encoding and Pillow image output): `python -m pip install -r requirements.txt`. Tk is used only for the desktop interface.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/09-qr-code-studio`. Activate your Python environment first.

## Open the desktop app

Double-click `desktop.pyw` on Windows (with Python file associations configured),
or run `python gui.py` from this project folder. The launcher uses the repository's
`.venv` when available, so it can find the installed QR dependencies. First-time
installation of `requirements.txt` is still required. The CLI below is unchanged.

1. Enter your text or link.
2. Pick **Small**, **Medium**, or **Large**, then a color style. Optional color
   pickers let you choose ink and paper colors without typing hex codes.
3. Click **Generate QR code**, check the preview, then **Save PNG image** or
   **Save SVG vector** and choose where to save it.

Sizes use 6, 10, or 16 pixels per module. Editing text or colors clears the old
preview and disables saving until a valid preview is generated. Invalid colors
show a useful message, and an existing file is never overwritten.

[Studio window](screenshots/app.png).

## Usage

```powershell
python main.py --gui
python main.py "https://www.python.org/" --output outputs/python.png
python main.py "Hello Python" --output outputs/hello.svg --size 12 --foreground "#172554" --background white
```

Module size is 2-30 pixels. PNG and SVG include a four-module quiet zone and medium error correction. The payload is limited to 1,200 UTF-8 bytes for practical readability. Dark foreground on a light background is required; the contrast check is a useful guardrail, not a guarantee that every scanner will work. Existing exports are protected: choose a new filename. The app never visits encoded URLs.

Verification: open the exported image at its intended size, scan it with a phone camera or an offline QR reader, and compare the complete decoded text or URL character for character. Test after printing or resizing too. Do not crop the quiet zone. Avoid entering secrets into public examples.

## Tests and representative output

```powershell
python -m unittest discover -s tests -v
```

[Application capture](screenshots/app.png). See [samples](samples/) for outputs from real execution and
[exercises](exercises.md) for follow-up challenges. The repository-wide test
command is `python scripts/run_project_tests.py` from the repository root.

## Troubleshooting

Install the project requirements if qrcode or Pillow is missing. For a Tk error, check `python -m tkinter`; use the CLI on headless systems. A contrast error needs darker modules or a lighter background. A save error may mean the output already exists. If scanning fails, use black on white, a larger module size, and a shorter message.


To exercise the click-through flows and regenerate the real captures, run
`python scripts/check_tool_guis.py` from the repository root. This optional
verification command uses the capture dependencies in
`scripts/requirements-verification.txt`; it stops its temporary local server.

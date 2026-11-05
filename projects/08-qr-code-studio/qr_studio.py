"""Validate QR settings once, then export the same matrix as PNG or SVG."""

from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from PIL import Image, ImageColor, ImageDraw
import qrcode
from qrcode.exceptions import DataOverflowError


def luminance(color: tuple[int, int, int]) -> float:
    channels = [value / 255 for value in color]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in channels]
    return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))


def validate_settings(text: str, scale: int, foreground: str, background: str) -> tuple:
    if not text.strip():
        raise ValueError("Enter text or a URL; the message cannot be blank.")
    if len(text.encode("utf-8")) > 1200:
        raise ValueError("Use at most 1,200 UTF-8 bytes for a practical, readable code.")
    if "://" in text or text.lower().startswith(("http:", "https:")):
        try:
            url = urlsplit(text)
            if url.scheme not in ("http", "https") or not url.hostname or any(c.isspace() for c in text):
                raise ValueError
            _ = url.port
        except ValueError:
            raise ValueError("URLs must use http:// or https:// with a valid host and port.") from None
    if not 2 <= scale <= 30:
        raise ValueError("Size must be 2-30 pixels per module.")
    try:
        dark, light = ImageColor.getrgb(foreground), ImageColor.getrgb(background)
    except ValueError:
        raise ValueError("Use color names or #RRGGBB colors.") from None
    if len(dark) != 3 or len(light) != 3:
        raise ValueError("Use opaque RGB colors, without transparency.")
    if luminance(dark) >= luminance(light) or (luminance(light) + 0.05) / (luminance(dark) + 0.05) < 4.5:
        raise ValueError("Choose dark modules on a light background with stronger contrast.")
    return dark, light


def make_matrix(text: str, scale: int = 10, foreground: str = "#172554",
                background: str = "white") -> list[list[bool]]:
    validate_settings(text, scale, foreground, background)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    qr.add_data(text)  # Preserve the exact payload, including intentional whitespace.
    try:
        qr.make(fit=True)
    except DataOverflowError:
        raise ValueError("This message is too large; shorten it.") from None
    return qr.get_matrix()


def render_png(matrix: list[list[bool]], scale: int, foreground: str, background: str) -> Image.Image:
    image = Image.new("RGB", (len(matrix) * scale, len(matrix) * scale), background)
    draw = ImageDraw.Draw(image)
    for row, values in enumerate(matrix):
        for column, filled in enumerate(values):
            if filled:
                draw.rectangle((column * scale, row * scale, (column + 1) * scale - 1,
                                (row + 1) * scale - 1), fill=foreground)
    return image


def export_qr(text: str, output: Path, *, scale: int = 10,
              foreground: str = "#172554", background: str = "white") -> Path:
    matrix = make_matrix(text, scale, foreground, background)
    if output.suffix.lower() not in (".png", ".svg"):
        raise ValueError("The output filename must end in .png or .svg.")
    # Exclusive creation protects an existing export from accidental replacement.
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".png":
        image = render_png(matrix, scale, foreground, background)
        with output.open("xb") as stream:
            image.save(stream, format="PNG")
    else:
        size = len(matrix) * scale
        svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(size), height=str(size),
                         viewBox=f"0 0 {len(matrix)} {len(matrix)}")
        ET.SubElement(svg, "rect", width="100%", height="100%", fill=background)
        path = " ".join(f"M{column},{row}h1v1h-1z" for row, values in enumerate(matrix)
                        for column, filled in enumerate(values) if filled)
        ET.SubElement(svg, "path", d=path, fill=foreground)
        with output.open("xb") as stream:
            ET.ElementTree(svg).write(stream, encoding="utf-8", xml_declaration=True)
    return output


class Studio:
    """Enter, preview, and save, with presets instead of mandatory color codes."""

    SIZES = {"Small": 6, "Medium": 10, "Large": 16}
    COLORS = {"Ocean": ("#172554", "#ffffff"), "Black and white": ("#111827", "#ffffff"),
              "Forest": ("#064e3b", "#f0fdf4")}

    def __init__(self, root):
        import tkinter as tk
        from tkinter import ttk

        self.root = root
        self.preview_signature = None
        self.photo = None
        root.title("QR Code Studio")
        root.geometry("980x770")
        root.minsize(930, 740)
        root.configure(background="#eef2f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="white")
        style.configure("Page.TLabel", background="#eef2f7", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Title.TLabel", background="#eef2f7", foreground="#0f172a", font=("Segoe UI", 26, "bold"))
        style.configure("Card.TLabel", background="white", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Step.TLabel", background="white", foreground="#0f172a", font=("Segoe UI", 13, "bold"))
        style.configure("Primary.TButton", background="#0f766e", foreground="white", font=("Segoe UI", 11, "bold"), padding=(16, 12))
        style.map("Primary.TButton", background=[("active", "#115e59"), ("disabled", "#94a3b8")])
        body = ttk.Frame(root, padding=26, style="Page.TFrame")
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="08 / TURN A MESSAGE INTO A SCAN", style="Page.TLabel").pack(anchor="w")
        ttk.Label(body, text="QR Code Studio", style="Title.TLabel").pack(anchor="w", pady=(6, 8))
        ttk.Label(body, text="Type it. Preview it. Save it.", style="Page.TLabel").pack(anchor="w")
        panels = ttk.Frame(body, style="Page.TFrame")
        panels.pack(fill="both", expand=True, pady=22)
        panels.columnconfigure(0, weight=1, uniform="panel")
        panels.columnconfigure(1, weight=1, uniform="panel")
        panels.rowconfigure(0, weight=1)
        inputs = ttk.Frame(panels, padding=20, style="Card.TFrame")
        inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        preview = ttk.Frame(panels, padding=20, style="Card.TFrame")
        preview.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(inputs, text="1. Enter text or a link", style="Step.TLabel").pack(anchor="w")
        self.message = tk.Text(inputs, height=5, width=32, wrap="word", font=("Segoe UI", 12), relief="solid", borderwidth=1)
        self.message.pack(fill="x", pady=(12, 22))
        self.message.insert("1.0", "https://www.python.org/")
        self.message.edit_modified(False)
        ttk.Label(inputs, text="2. Pick the look", style="Step.TLabel").pack(anchor="w")
        self.scale = tk.IntVar(value=10)
        self.foreground = tk.StringVar(value="#172554")
        self.background = tk.StringVar(value="#ffffff")
        self.size_choice = tk.StringVar(value="Medium")
        self.color_choice = tk.StringVar(value="Ocean")
        for label, variable, options, handler in (
            ("Size", self.size_choice, list(self.SIZES), self.change_size),
            ("Color style", self.color_choice, list(self.COLORS), self.change_colors),
        ):
            group = ttk.Frame(inputs, style="Card.TFrame")
            group.pack(fill="x", pady=(12, 0))
            ttk.Label(group, text=label, style="Card.TLabel", width=12).pack(side="left")
            selector = ttk.Combobox(group, textvariable=variable, values=options, state="readonly", width=20)
            selector.pack(side="left", fill="x", expand=True)
            selector.bind("<<ComboboxSelected>>", handler)
        custom = ttk.Frame(inputs, style="Card.TFrame")
        custom.pack(fill="x", pady=16)
        ttk.Button(custom, text="Ink color...", command=lambda: self.pick_color(self.foreground)).pack(side="left")
        ttk.Button(custom, text="Paper color...", command=lambda: self.pick_color(self.background)).pack(side="left", padx=8)
        self.generate_button = ttk.Button(inputs, text="Generate QR code", command=self.preview, style="Primary.TButton")
        self.generate_button.pack(fill="x", pady=(8, 12))
        ttk.Label(inputs, text="Everything is generated on your computer. No sign-in or online service needed.",
                  style="Card.TLabel", wraplength=360).pack(anchor="w", pady=8)
        ttk.Label(preview, text="3. Preview and save", style="Step.TLabel").pack(anchor="w")
        self.preview_label = ttk.Label(preview, style="Card.TLabel", anchor="center")
        self.preview_label.pack(fill="both", expand=True, pady=12)
        self.status = ttk.Label(preview, style="Card.TLabel", wraplength=360)
        self.status.pack(anchor="w", pady=(0, 14))
        save_row = ttk.Frame(preview, style="Card.TFrame")
        save_row.pack(fill="x")
        self.save_buttons = []
        for extension, label in (("png", "Save PNG image"), ("svg", "Save SVG vector")):
            button = ttk.Button(save_row, text=label, command=lambda kind=extension: self.save(kind), padding=10)
            button.pack(side="left", fill="x", expand=True, padx=(0, 6))
            self.save_buttons.append(button)
        ttk.Label(body, text="Scan the saved code and check its text before sharing. Existing files are never overwritten.",
                  style="Page.TLabel", wraplength=900).pack(anchor="w")
        for variable in (self.scale, self.foreground, self.background):
            variable.trace_add("write", self.invalidate_preview)
        self.message.bind("<<Modified>>", self.message_changed)
        self.preview()

    def values(self) -> tuple:
        return (self.message.get("1.0", "end-1c"), self.scale.get(), self.foreground.get(), self.background.get())

    def invalidate_preview(self, *_):
        self.preview_signature = None
        self.photo = None
        self.preview_label.configure(image="", text="Your preview will appear here.")
        self.status.configure(text="Click Generate QR code to preview these settings.", foreground="#334155")
        for button in self.save_buttons:
            button.configure(state="disabled")

    def message_changed(self, _event=None):
        if self.message.edit_modified():
            self.message.edit_modified(False)
            self.invalidate_preview()

    def change_size(self, _event=None):
        self.scale.set(self.SIZES[self.size_choice.get()])

    def change_colors(self, _event=None):
        foreground, background = self.COLORS[self.color_choice.get()]
        self.foreground.set(foreground)
        self.background.set(background)

    def pick_color(self, variable):
        from tkinter import colorchooser
        _rgb, color = colorchooser.askcolor(parent=self.root, initialcolor=variable.get(), title="Choose a QR color")
        if color:
            variable.set(color)

    def preview(self) -> bool:
        from PIL import ImageTk
        from tkinter import TclError
        self.invalidate_preview()
        try:
            settings = self.values()
            text, scale, foreground, background = settings
            matrix = make_matrix(text, scale, foreground, background)
            image = render_png(matrix, scale, foreground, background)
            image.thumbnail((320, 320), Image.Resampling.NEAREST)
            self.photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.photo, text="")
            self.preview_signature = settings
            self.status.configure(text=f"Ready: {len(matrix) * scale} x {len(matrix) * scale} pixels. Choose a format to save.", foreground="#047857")
            for button in self.save_buttons:
                button.configure(state="normal")
            return True
        except (ValueError, TclError) as exc:
            self.status.configure(text=f"Check your settings: {exc}", foreground="#b45309")
            return False

    def save(self, extension: str) -> None:
        from tkinter import TclError, filedialog
        try:
            # Revalidate even if a text-change event has not yet been delivered.
            if self.values() != self.preview_signature and not self.preview():
                return
            text, scale, foreground, background = self.preview_signature
            filename = filedialog.asksaveasfilename(parent=self.root, initialfile=f"my-qr.{extension}",
                                                   defaultextension=f".{extension}",
                                                   filetypes=[(extension.upper(), f"*.{extension}")])
            if not filename:
                return
            export_qr(text, Path(filename), scale=scale, foreground=foreground, background=background)
            self.status.configure(text=f"Saved {Path(filename).name}.", foreground="#047857")
        except FileExistsError:
            self.status.configure(text="That file already exists. Choose a new filename to keep both copies.", foreground="#b45309")
        except (OSError, ValueError, TclError) as exc:
            self.status.configure(text=f"Could not save: {exc}", foreground="#b45309")

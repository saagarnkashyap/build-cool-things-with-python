# Manuscript production report

## Deliverable and scope

- File: `Build_Cool_Things_with_Python_Manuscript.docx`
- Working title: *Build Cool Things with Python: From Zero to Real-World Builder*
- Repository inspected at Git commit `00201db` on 2026-11-05.
- Word document: 16,963 words, 10 project chapters, Chapter 0, a concluding Chapter 11, front matter, and six appendices.
- Figures: 10 verified project captures. Teaching listings: 38 short examples and commands.
- Page target: approximately 260. Actual Microsoft Word-rendered page count: **71** (189 fewer than the target).

The document is a complete first-pass manuscript by section and chapter coverage,
but it is not yet a 260-page publication manuscript. Its actual length is a
material shortfall. Page allocations were not filled with blank pages or
duplicate source listings.

## Project inventory and entry points

Commands below are written from the repository root. They were checked against
the current files and project documentation. Previous local verification records
show 66 unit/UI tests across eight suites, 15 visual-art checks, and 22 launch,
export, and dashboard checks. The repository was not rerun for this production
task because the supplied prompt requires read-only inspection.

| Book chapter | Project directory | Actual entry point and launch command | Runtime dependency |
| --- | --- | --- | --- |
| 1 | `projects/01-number-guessing` | `python projects/01-number-guessing/main.py`; desktop `gui.py` | Standard library; Tk for desktop |
| 2 | `projects/02-rock-paper-scissors` | `python projects/02-rock-paper-scissors/main.py`; desktop `gui.py` | Standard library; Tk for desktop |
| 3 | `projects/03-password-generator` | `python projects/03-password-generator/main.py`; desktop `gui.py` | Standard library; Tk for desktop |
| 4 | `projects/visual-art-lab/05-heartglow` | `python projects/visual-art-lab/05-heartglow/love.py` | Standard library with Tk/Turtle |
| 5 | `projects/visual-art-lab/04-bloomcraft` | `python projects/visual-art-lab/04-bloomcraft/flow.py` | Pillow, NumPy, Tk for desktop |
| 6 | `projects/visual-art-lab/06-spiral-ink` | `python projects/visual-art-lab/06-spiral-ink/pic2.py`; shared `spiral_art.py` | Pillow; Tk for desktop |
| 7 | `projects/07-smart-file-organizer` | `python projects/07-smart-file-organizer/main.py --gui`; CLI preview in `main.py` | Standard library; Tk for desktop |
| 8 | `projects/08-qr-code-studio` | `python projects/08-qr-code-studio/main.py --gui` | `qrcode[pil]`, Pillow; Tk for desktop |
| 9 | `projects/09-expense-tracker-dashboard` | `python -m streamlit run projects/09-expense-tracker-dashboard/app.py --server.address 127.0.0.1`; desktop launcher `gui.py` | Streamlit, Pandas; Tk for launcher |
| 10 | `projects/10-maze-solving-visualizer` | `python projects/10-maze-solving-visualizer/main.py --predefined`; terminal `--solve` | Standard library; Tk for desktop |

The book outline assigns Heartglow Chapter 4 and Bloomcraft Chapter 5. Their
existing folder prefixes are respectively `05` and `04`; every manuscript
command uses the actual directory. The imported Bloomcraft README mentions
`flower.py`, but the present entry point is `flow.py`. The password project has
no implemented strength checker. The chapter discusses the limits of estimating
password strength and states that the feature does not exist.

## Figure source record

All figures are embedded in the DOCX and carry descriptive alt text. These
source files were read, not changed. Figure 8 is a crop of the authentic capture
made in memory during document generation; the crop excludes its QR preview and
outdated chapter badge. No cropped image was written into the repository.

| Figure | Source file |
| --- | --- |
| 1 | `projects/01-number-guessing/screenshots/app.png` |
| 2 | `projects/02-rock-paper-scissors/screenshots/app.png` |
| 3 | `projects/03-password-generator/screenshots/app.png` |
| 4 | `research/runtime-checks/heartglow-window.png` |
| 5 | `research/runtime-checks/bloomcraft-render.png` |
| 6 | `research/runtime-checks/lilies-window.png` |
| 7 | `projects/07-smart-file-organizer/screenshots/app.png` |
| 8 | `projects/08-qr-code-studio/screenshots/app.png` (crop of controls) |
| 9 | `projects/09-expense-tracker-dashboard/screenshots/app.png` |
| 10 | `projects/10-maze-solving-visualizer/screenshots/app.png` |

The three visual-art images are saved frames or captures from the existing
runtime-check records. Figure 6 incorporates the supplied pink-lilies photo.
The full expense-dashboard capture is legible on screen but may need a dedicated
high-resolution crop before print publication.

## Rights, credits, and editorial issues

The repository's `research/license-audit.md` records no license declaration in
the three imported visual project snapshots. Code ownership, adaptation,
redistribution, and textbook inclusion permissions have not been independently
verified. The source and reproduction permissions for the supplied photographs
and selected visual screenshots also remain open. Confirm rights and required
credits before publishing this draft. No unsupported personal author credit,
publisher, ISBN, endorsement, or copyright holder was inserted.

The manuscript contains a textual placeholder for companion repository access.
No repository address, external URL, live hyperlink, or QR symbol was inserted.
The contents page is a static, non-clickable list with page numbers verified
against the final Word render. It is not automatically updating; after editing,
refresh the numbers manually or insert a new automatic Word table of contents
from the existing Heading styles. An automatic field was tried during QA but
made Word repeatedly recalculate the document, so it was removed. This is a
remaining production limitation. Python 3.12 syntax was
checked in prior repository verification, but this manuscript production run
used the existing Python 3.14 environment and did not execute all projects anew.

## Quality assurance

- The DOCX was created as editable Word paragraphs, styles, tables, and images;
  text and code were not flattened into a picture.
- Heading 1, Heading 2, and Heading 3 styles, A4 pages, running header,
  page-number field, section breaks, captions, and monospaced listings are present.
- The package contains ten embedded image parts and ten alt-text descriptions.
- The DOCX package inspection found no external relationship targets or Word
  hyperlink elements. Manuscript text was checked for web-address patterns.
- Each of the ten project chapters includes the required A–L teaching sections,
  four to six objectives, and three graded challenges.
- No complete project source listing is reproduced.
- A repository-content digest before and after creation, excluding `output`,
  Git metadata, environments, caches, and prior generated outputs, matched:
  184 files, SHA-256 `bca890e6b4ac5e0b1e80749d8a10a05d65ce00a9abb750f98351b84b329864f8`.
- `git status --short` showed only `?? output/` after generation.
- Microsoft Word opened a temporary copy and rendered it to a temporary PDF:
  71 pages. The contents, a foundation chapter page, the cropped QR chapter
  figure, and the ending page were visually inspected. All 71 pages contain
  content; no accidental blank pages remain. The PDF and PNG previews were kept
  outside the repository and are not deliverables.

The manuscript is a working publication draft. Before release, expand lessons
substantially toward the 260-page editorial goal, resolve image/code rights,
confirm author and publication metadata, convert the static contents to an
automatic Word table if required, and commission a human technical and copy
edit.

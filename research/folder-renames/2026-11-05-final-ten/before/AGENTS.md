# Repository conventions

- Target Python 3.12 or later. Keep each numbered project independently runnable.
- Preserve completed projects and user artwork unless the task explicitly changes them.
- Separate input/output code from small, testable functions. Prefer the standard
  library; document every external runtime dependency in project requirements.
- Use descriptive snake_case names, four-space indentation, and helpful type hints.
  Explain non-obvious decisions; avoid comments that repeat the code.
- New implementations and exercises must be written for this project. Preserve
  applicable upstream notices and accurate license records. Do not invent authorship.
- Never delete user files automatically. File operations must have a preview,
  avoid overwriting, and validate paths and recovery data before acting.
- Test normal behavior, boundaries, invalid inputs, and failure recovery. Use
  temporary directories and synthetic fixtures, never personal data or live services.
- Each project needs a README (objectives, installation, run/test commands,
  examples, troubleshooting), three exercise levels, sample output, and genuine
  captures or terminal transcripts. Keep published examples free of secrets.
- Run `python scripts/run_project_tests.py` for the new numbered projects.
  Visual Art Lab has its own existing checks; do not rewrite it as part of routine work.
- Record verification accurately, including untested platforms and failed checks.
- Do not generate manuscript or publisher artifacts unless explicitly requested.

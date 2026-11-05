# New project and dependency records

Recorded: 2026-11-05. Scope: numbered projects 01, 02, 03, 07, 09, 11, and 16.

The new implementation files, exercises, synthetic CSV, and test fixtures were
written for this repository. They do not copy implementation files or artwork
from the reference clone. This record does not assign personal sole authorship
or apply a new license to the repository's existing imported work.

## Requested reference clone

A public beginner repository was found and cloned into the ignored directory
`research/reference-repositories/python-starter-lab/`. Its MIT license and
copyright notice remain intact in that clone. Its source is not part of the new
project implementations. The exact URL and commit are in
[reference-repository.json](verification/reference-repository.json).

## External packages

Packages are installed as dependencies, not vendored source. Their notices and
licenses remain in their distributions. Runtime requirements specify supported
version ranges; exact verification versions are recorded separately.

| Package | Purpose | License record |
| --- | --- | --- |
| [qrcode](https://pypi.org/project/qrcode/) | QR encoding | BSD-3-Clause; retain package notices when redistributing |
| [Pillow](https://pillow.readthedocs.io/en/stable/about.html#license) | QR PNG output; optional capture utilities | MIT-CMU; see package license |
| [Streamlit](https://github.com/streamlit/streamlit/blob/develop/LICENSE) | Expense dashboard and AppTest | Apache-2.0 |
| [Pandas](https://pandas.pydata.org/docs/getting_started/overview.html#license) | Expense tables and summaries | BSD-3-Clause |
| [Playwright](https://github.com/microsoft/playwright/blob/main/LICENSE) | Optional browser screenshot verification | Apache-2.0 |
| [zxing-cpp](https://github.com/zxing-cpp/zxing-cpp/blob/master/LICENSE) | Optional independent QR decoding | Apache-2.0 |

The existing Visual Art Lab code and requester-supplied JPEGs keep their prior
provenance and unresolved permission status in [license-audit.md](license-audit.md).
A preservation digest was taken before work and checked afterward. New sample
expense rows contain only fictional categories and descriptions, with no personal
information. New screenshots show only local application fixtures and public
demonstration content.

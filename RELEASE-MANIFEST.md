# Release manifest

## GitHub repository (this folder)

- `README.md`, `LICENSE` (GPLv3), `.gitignore`, `RELEASE-MANIFEST.md`
- `paper/rcf.tex`, `paper/references.bib`, `paper/rcf.bbl`, `paper/tables/table_*.tex` (5), `paper/figures/field.pdf`, `paper/rcf.pdf` (compiled with XeLaTeX via Tectonic; the sources are pdflatex-compatible, and arXiv's own pdflatex build may break pages slightly differently, so the page count in the metadata must be confirmed on arXiv's preview before submission)
- `anc/`: `pyproject.toml`, `README.md`, `rcf/__init__.py`, `rcf/field.py`, `tests/test_field.py`, `examples/worked_example.py`
- `arxiv_submission/arxiv_metadata.md` (a preparation note)

## arXiv source upload (one archive, compiled by arXiv with pdflatex)

- `rcf.tex`, `references.bib`, `rcf.bbl` (generated from references.bib by the compile; arXiv compiles with the .bbl), `tables/` (5 files), `figures/field.pdf`
- `anc/` as ancillary files: the reference implementation, tests and reproduction script

## Release boundary

Only the files listed in this manifest are part of this release.

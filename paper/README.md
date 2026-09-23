# Manuscript

`main.tex` is the paper: market structure in European electricity and gas, 2013–2023, with Germany as the reference country.

Figures are the PNGs written by `scripts/run_pipeline.py` to `output/figures/`. Citations are in `references.bib`. Every entry is a Eurostat or European Environment Agency page that was opened on 23 September 2026.

`Research_Paper_Word_Version.md` is an earlier draft. It is withdrawn. Do not cite it.

Compile from this directory:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

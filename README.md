# Market structure in European electricity and gas, 2013–2023

Germany in comparative perspective. The study describes electricity-market concentration and gas-retailer density. It does not measure prices, grid quality, or social cohesion, and it does not evaluate a policy.

The manuscript is `paper/main.tex`. Variable definitions are in `CODEBOOK.md`. Computed results are in `output/RESULTS.md`.

## What the series are

| Code | What it is |
|---|---|
| `CMPY_ECAP5` | Cumulative share of electricity capacity held by firms with at least 5% |
| `CMPY_EG5` | Cumulative share of electricity generation held by firms with at least 5% |
| `LCMPY_IECAP`, `LCMPY_EG` | Share of the single largest firm, capacity and generation |
| `GRTL` | Number of gas retailers |

Earlier drafts called the first two series prices and called `GRTL` grid infrastructure. Those labels were wrong. Documents that still use them are withdrawn. The manuscript supersedes them.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python scripts/run_pipeline.py
```

The script reads `estat_nrg_ind_market.tsv`, downloads final natural-gas consumption (`nrg_bal_s`, `FC_E` + `FC_NE`) and population on 1 January (`demo_pjan`), and writes the panel, tables, and figures. Pass `--refresh` to download the Eurostat supplements again.

Compile the paper from `paper/`:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Main results

Germany’s cumulative capacity share fell from 67.0% in 2013 to 52.5% in 2023, and its cumulative generation share fell from 74.0% to 57.1%. The cross-country medians fell too, and Germany stayed near the middle of both rankings. Germany ranked first on the raw count of gas retailers in 2023 (973) and 11th of 30 on retailers per terawatt-hour.

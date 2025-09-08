# Appendix: Code, Tables, and Figures

## A. Code Inventory

- scripts/clean_eurostat_tsv.py — Clean and reshape Eurostat TSV to wide/long CSV.
- scripts/quality_report.py — Data quality profiling (missingness, ranges, uniques).
- scripts/build_master_dataset.py — Derived indicators and master dataset creation.
- scripts/simple_analysis.py — Descriptive stats using csv + statistics.
- scripts/regression_analysis.py — Simple linear regression & correlations.
- scripts/visualization_analysis.py — ASCII visualizations and trend tables.

## B. Data Files

- data/estat_nrg_ind_market_wide.csv — Cleaned wide format.
- data/estat_nrg_ind_market_long.csv — Cleaned long format.
- data/master_dataset.csv — Final analysis dataset.
- data/analysis_results/ — Generated reports (simple, regression, visualization).

## C. Key Tables

- Descriptive statistics per variable and year.
- Correlation matrix for core indicators.
- Regression line estimates for simple models.

## D. Figures (ASCII)

- Germany GRTL_NR time series (2013–2024).
- Country comparison bars (mean GRTL_NR, top countries).
- Correlation heatmap (symbolic density).

## E. Reproducibility Notes

- Environment: Python 3 (standard library). No external packages required.
- Entry points:
  - python scripts/simple_analysis.py
  - python scripts/regression_analysis.py
  - python scripts/visualization_analysis.py
- Outputs are saved to data/analysis_results.

## F. Known Limitations

- No pandas/statsmodels due to environment constraints.
- Correlational only; no causal identification.
- ASCII figures for portability.




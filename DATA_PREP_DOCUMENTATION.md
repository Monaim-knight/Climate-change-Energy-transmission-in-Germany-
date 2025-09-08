# Data Preparation Documentation (Phase 3)

## Files and Scripts
- Raw input: `estat_nrg_ind_market.tsv`
- Cleaner: `scripts/clean_eurostat_tsv.py`
  - Outputs: `data/estat_nrg_ind_market_wide.csv`, `data/estat_nrg_ind_market_long.csv`
- Quality report: `scripts/quality_report.py`
  - Outputs (console): row counts, missingness, ranges, uniques
- Master builder: `scripts/build_master_dataset.py`
  - Output: `data/master_dataset.csv`

## Processing Steps
1. Parse Eurostat TSV
   - Split meta columns: `freq,siec,indic_nrgm,unit,geo`
   - Spread years to columns (wide) and normalize to `year,value` (long)
   - Treat `:` as missing
2. Quality profiling
   - Long: 8,472 rows; 945 missing values; min −4791, max 22,762; 36 geos; 20 indicators; 3 units
   - Wide: 706 rows; 17 columns; 2024 largely missing (expected)
3. Harmonization keys
   - Time: `year` (2013–2024 as available)
   - Geography: `geo` (country codes); future NUTS mapping possible
4. Derived indicators + master dataset
   - Selected indicators pivoted as features (subset)
   - Example derived: `DERIV_energy_price_gap_PC = CMPY_ECAP5_PC − CMPY_EG5_PC`
   - Saved to `data/master_dataset.csv`

## Outputs
- `data/estat_nrg_ind_market_wide.csv`
- `data/estat_nrg_ind_market_long.csv`
- `data/master_dataset.csv`

## Notes
- Missing values are empty strings in CSV outputs
- Indicators kept in master are a starting subset; extend as needed
- When adding Destatis/SOEP/BNetzA, use `HARMONIZATION_KEYS.md` for alignment

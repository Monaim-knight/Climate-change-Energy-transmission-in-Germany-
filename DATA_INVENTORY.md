# Data Inventory (Phase 3)

Variable definitions in this note are withdrawn. Use `CODEBOOK.md`. Destatis, SOEP, Bundesnetzagentur, dena, and UBA are not part of the approved study. The study uses Eurostat `nrg_ind_market` plus, at the next step, final natural-gas consumption and population.

## Eurostat
- Source: Eurostat (energy market indicators)
- Raw: `estat_nrg_ind_market.tsv`
- Cleaned (wide): `data/estat_nrg_ind_market_wide.csv`
- Cleaned (long): `data/estat_nrg_ind_market_long.csv`
- Coverage: 2013–2024 (years as available), geo = country codes (AT, DE, ...)
- Variables: freq, siec, indic_nrgm, unit, geo, year/value (long)
- Missing: `:` mapped to empty string

## Destatis (placeholder)
- Source: Statistisches Bundesamt
- Planned: Energy price indices, household expenditure, regional stats
- Status: Pending access/download

## SOEP (placeholder)
- Source: DIW Berlin
- Planned: Trust, social participation, demographics, income
- Status: License request pending

## BNetzA (placeholder)
- Source: Bundesnetzagentur
- Planned: Grid, installations, regional prices/charges
- Status: To fetch

## dena / UBA (placeholder)
- Source: dena, UBA
- Planned: Energiewende indicators, environmental indicators
- Status: To fetch

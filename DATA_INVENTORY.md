# Data Inventory (Phase 3)

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

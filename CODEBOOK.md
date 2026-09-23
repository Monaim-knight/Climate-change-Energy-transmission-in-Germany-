# Codebook

Locked to the research contract approved 23 September 2026. This file is the authority for what each series means. Comments in `scripts/build_master_dataset.py` still use the old labels (price competitiveness, grid, low-carbon). Those comments are obsolete. The pipeline rewrite comes later; until then, read this file.

Source of record: `estat_nrg_ind_market.tsv` (Eurostat energy market indicators, table `nrg_ind_market`). Frequency `A` (annual). `data/estat_nrg_ind_market_long.csv` and `data/estat_nrg_ind_market_wide.csv` are reshapes of that file. `data/master_dataset.csv` keeps only four indicators plus one retired field. New work reads the long file.

Indicator labels are the Eurostat vocabulary `indic_nrgm` (EEA data dictionary, status valid 17 May 2021). That vocabulary has no prose definitions. The share-versus-count reading below is fixed from the unit code and from the unit-check row.

## Identifiers

| Field | Values in this extract | Meaning |
|---|---|---|
| `geo` | Eurostat country code | One row is a country. There is no EU or euro-area aggregate in this file. |
| `year` | 2013–2024 | Analysis window is 2013–2023. Column 2024 is dropped. |
| `siec` | `E7000`, `G3000` | `E7000` electricity. `G3000` natural gas. |
| `unit` | `PC`, `NR`, `MW` | `PC` percent. `NR` a count. `MW` megawatts. |
| `indic_nrgm` | 20 codes | See the tables below. |
| `value` | number or blank | Eurostat `:` is stored as blank. Blank is not zero. |

### How to read a percent versus a count

`PC` is a share on a 0–100 scale. `NR` is a count of firms. The same country-year shows why the old labels cannot stand:

| Series | Germany, 2013 | Reading |
|---|---|---|
| `CMPY_ECAP5` (`PC`) | 67 | Cumulative capacity share of companies that each hold at least 5% |
| `LCMPY_IECAP` (`PC`) | 29 | Capacity share of the single largest company |
| `CMPY_EG5` (`PC`) | 74 | Cumulative generation share of companies that each hold at least 5% |
| `LCMPY_EG` (`PC`) | 32 | Generation share of the single largest company |
| `GRTL` (`NR`) | 825 | Number of gas retailers |

The group share is larger than the largest firm in both electricity margins. That is what a cumulative share does. It is not a price, and 825 is not a grid-quality index.

## Study series

These are the series named in the contract. `LCMPY_IECAP` is in because its unit in this extract is `PC`, which was the condition for using it. `LCMPY_EG` is the generation-side twin: it sits in the same table so the 74% generation figure is not read as one company. It is not a new research question.

| Code | Unit | Product | Official label | Role in the paper |
|---|---|---|---|---|
| `CMPY_ECAP5` | PC | Electricity (`E7000`) | Companies with at least 5% of the electricity capacity | RQ1. Cumulative capacity share of firms at or above 5%. Already a share, so it is not rescaled. |
| `CMPY_EG5` | PC | Electricity (`E7000`) | Companies with at least 5% of the electricity generation | RQ1. Cumulative generation share of firms at or above 5%. Electricity, not gas. |
| `LCMPY_IECAP` | PC | Electricity (`E7000`) | Largest company — installed electricity capacity | Companion to `CMPY_ECAP5`. Share of the largest firm only. |
| `LCMPY_EG` | PC | Electricity (`E7000`) | Largest company — electricity generation | Companion to `CMPY_EG5`. Same reading, generation side. |
| `GRTL` | NR | Natural gas (`G3000`) | Gas retailers | RQ2, as an input to density. The raw count is reported only to show market size. Ranks use retailers per TWh. |

Storage names in `data/master_dataset.csv`: `CMPY_ECAP5_PC`, `CMPY_EG5_PC`, `LCMPY_IECAP_PC`, `GRTL_NR`. `LCMPY_EG` is in the long file and is absent from the master file.

### Coverage inside 2013–2023

Germany reports every year 2013–2023 on all five series. 2024 is almost empty (North Macedonia on the electricity series; Spain and North Macedonia on `GRTL`) and is not used.

| Series | Countries with at least one year | Countries absent |
|---|---|---|
| `CMPY_ECAP5`, `CMPY_EG5` | 35 | Norway |
| `LCMPY_IECAP`, `LCMPY_EG` | 32 | Norway, Austria, the Netherlands, Turkey |
| `GRTL` | 34 | Malta, Norway |

The country set is whoever reports the series. It is not a fixed EU27 panel. Each table will state its own N.

## Constructed variables

Built by `scripts/run_pipeline.py`. Eurostat’s simplified balance (`nrg_bal_s`) has no single code `FC`. Final consumption is the sum of the two published components.

| Name | Formula | Rule |
|---|---|---|
| `gas_fc_gwh` | `FC_E + FC_NE` from `nrg_bal_s`: annual, natural gas (`G3000`), gigawatt-hours. `FC_E` is final consumption — energy use. `FC_NE` is final consumption — non-energy use. Join on `geo` + `year`. | Denominator for RQ2. If either component is missing, the sum is missing. |
| `retailers_per_twh` | `GRTL / (gas_fc_gwh / 1000)` | Headline gas-retail measure. Retailers per terawatt-hour of final consumption. |
| `in_density_sample` | `gas_fc_gwh >= 1000` and retailer count observed | Country-years under 1 TWh are out of the density ranking and listed in `output/tables/table_rq2_excluded.csv`. The threshold is fixed here, before any rank is computed. |
| `pop` | Eurostat population on 1 January (`demo_pjan`, total, number of persons). Join on `geo` + `year`. | Robustness denominator only: retailers per million inhabitants, on the same country-years that pass the 1 TWh screen. |

`DERIV_energy_price_gap_PC` in the master file equals `CMPY_ECAP5_PC − CMPY_EG5_PC`. It is the gap between two electricity-concentration shares. It is retired and will not appear in a table.

## In the extract, not in RQ1–RQ3

Recorded so they are not renamed into the study later. Twenty indicator codes, one product each, except `CMPY_NG5`, which is stored both as a count and as a percent.

**Electricity (`E7000`)**

| Code | Unit | Official label | Why it stays out |
|---|---|---|---|
| `PCMPY_NEG5` | NR | Companies producing at least 5% of net electricity generation | Count of firms, not the share used in RQ1. |
| `RCMPY_NEG95` | NR | Companies representing at least 95% of net electricity generation | Different threshold (95% of generation). |
| `ERTL` | NR | Electricity retailers | Retail count for electricity. A parallel to `GRTL`, not part of RQ2. |
| `ERTL_SELL_EC5` | NR | Electricity retailers selling at least 5% of total electricity consumed | Count of main retailers. |
| `ERTL_EC5` | PC | Electricity retailers with at least 5% of total electricity consumed | Retail concentration, electricity. |
| `ERTL_LG` | PC | Largest electricity retailer | Top-firm retail share, electricity. |
| `ECAP_CN` | MW | New electricity capacity connected | A capacity flow, not a market share. |
| `ECAP_DC` | MW | Electricity capacity decommissioned | A capacity flow. |
| `ECAP_VAR` | MW | Electricity capacity variation | A capacity flow. |

**Natural gas (`G3000`)**

| Code | Unit | Official label | Why it stays out |
|---|---|---|---|
| `GRTL_SELL_NG5` | NR | Gas retailers selling at least 5% of total natural gas consumed | Count of main retailers, not total retailers. |
| `GRTL_NG5` | PC | Gas retailers with at least 5% of total natural gas consumed | Gas retail concentration. |
| `GRTL_LG` | PC | Largest gas retailer | Top-firm gas retail share. |
| `CMPY_NG` | NR | Companies bringing natural gas | Importing or wholesale shippers, not retailers. |
| `CMPY_NG5` | NR and PC | Companies bringing at least 5% of the natural gas | Upstream concentration. Two units: do not collapse them. |
| `CMPY_LNG` | PC | Company bringing the largest amount of the natural gas | Top shipper’s share. |

## Geography

Codes that are easy to misread:

| Code | Country |
|---|---|
| `DE` | Germany |
| `EL` | Greece |
| `GE` | Georgia |
| `XK` | Kosovo |

Also in the file, outside the EU: Bosnia and Herzegovina (`BA`), Moldova (`MD`), Montenegro (`ME`), North Macedonia (`MK`), Serbia (`RS`), Turkey (`TR`), plus Norway where a series exists. The United Kingdom is not in this extract. `GE` is Georgia and must not be folded into Germany.

## Missing values and samples

- Blank means the TSV had `:`. Eurostat uses that mark for unavailable and for confidential. This extract does not say which. Leave blanks as missing.
- A reported `0` is a real zero. Cyprus has years of `GRTL` equal to 0. Those stay zero and still face the 1 TWh screen on the density ranking.
- Descriptive charts for RQ1 use every non-missing country-year of that series in 2013–2023.
- The RQ2 ranking uses country-years with both `GRTL` and `gas_fc_gwh`, and with final consumption of at least 1 TWh.
- The exploratory regression (RQ3) uses the common sample: non-missing generation concentration (`CMPY_EG5`), non-missing retailer density, and the 1 TWh screen. The table states how many country-years that drops relative to the descriptive samples.
- No observation is filled in by interpolation.

## Names that are withdrawn

| Old name in the repo | What the series actually is |
|---|---|
| Electricity price competitiveness | `CMPY_ECAP5`: cumulative electricity-capacity share |
| Gas price competitiveness | `CMPY_EG5`: cumulative electricity-generation share |
| Energy price gap | Difference of those two shares. Retired. |
| Grid infrastructure / grid-related indicator | `GRTL`: number of gas retailers |
| Low-carbon electricity indicator | `LCMPY_IECAP`: largest firm’s share of installed capacity |

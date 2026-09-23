#!/usr/bin/env python3
"""Rebuild the country-year panel and the RQ1–RQ3 exhibits.

Reads estat_nrg_ind_market.tsv. Joins Eurostat final natural-gas consumption
(nrg_bal_s: FC_E + FC_NE) and population on 1 January (demo_pjan).

  python3 -m venv .venv
  .venv/bin/pip install -r requirements-analysis.txt
  .venv/bin/python scripts/run_pipeline.py

Pass --refresh to re-download the Eurostat supplements.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
TSV_PATH = ROOT / "estat_nrg_ind_market.tsv"
EXTERNAL = ROOT / "data" / "external"
ANALYSIS = ROOT / "data" / "analysis"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

YEAR_MIN, YEAR_MAX = 2013, 2023
GAS_FLOOR_GWH = 1000.0
SHARE_FLAT_PP = 2.0
DENSITY_FLAT_REL = 0.10
LOO_BAND = 0.50
MIN_YEARS_FOR_FE = 2

# Cumulative >=5% shares are the RQ1 outcomes. Top-firm shares are companions.
SHARE_SERIES = {
    "e_cap_share": "Cumulative capacity share of firms with at least 5% (CMPY_ECAP5)",
    "e_gen_share": "Cumulative generation share of firms with at least 5% (CMPY_EG5)",
    "e_cap_top": "Largest firm's capacity share (LCMPY_IECAP)",
    "e_gen_top": "Largest firm's generation share (LCMPY_EG)",
}

KEEP = {
    ("CMPY_ECAP5", "PC", "E7000"): "e_cap_share",
    ("CMPY_EG5", "PC", "E7000"): "e_gen_share",
    ("LCMPY_IECAP", "PC", "E7000"): "e_cap_top",
    ("LCMPY_EG", "PC", "E7000"): "e_gen_top",
    ("GRTL", "NR", "G3000"): "gas_retailers",
}

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def fetch_jsonstat(dataset: str, params: dict) -> dict:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{EUROSTAT}/{dataset}?format=JSON&lang=EN&{query}"
    with urllib.request.urlopen(url, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def jsonstat_frame(payload: dict, value_name: str) -> pd.DataFrame:
    dim_ids = payload["id"]
    sizes = payload["size"]
    codes = []
    for dim_id in dim_ids:
        index = payload["dimension"][dim_id]["category"]["index"]
        if isinstance(index, dict):
            ordered = [None] * len(index)
            for code, pos in index.items():
                ordered[int(pos)] = code
        else:
            ordered = list(index)
        codes.append(ordered)
    status = payload.get("status") or {}
    rows = []
    for flat, value in payload["value"].items():
        flat_i = int(flat)
        coords = []
        rem = flat_i
        for size in reversed(sizes):
            coords.append(rem % size)
            rem //= size
        coords.reverse()
        row = {dim_id: code_list[pos] for dim_id, code_list, pos in zip(dim_ids, codes, coords)}
        row[value_name] = float(value)
        row["status"] = status.get(str(flat_i), status.get(flat, ""))
        rows.append(row)
    return pd.DataFrame(rows)


def load_market(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8").splitlines()
    years = [int(h.strip()) for h in lines[0].split("\t")[1:] if h.strip()]
    records = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        freq, siec, indic, unit, geo = [piece.strip() for piece in parts[0].split(",")]
        key = (indic, unit, siec)
        if key not in KEEP:
            continue
        for i, year in enumerate(years):
            raw = parts[1 + i].strip().replace(" ", "") if i + 1 < len(parts) else ""
            if raw.startswith(":"):
                raw = ":"
            elif raw.endswith(("p", "e", "d", "b", "u", "c")) and raw[:-1].replace(".", "", 1).replace("-", "", 1).isdigit():
                raw = raw[:-1]
            value = np.nan if raw in {"", ":"} else float(raw)
            records.append(
                {
                    "geo": geo,
                    "year": year,
                    "column": KEEP[key],
                    "value": value,
                }
            )
    long = pd.DataFrame(records)
    if long.duplicated(["geo", "year", "column"]).any():
        raise ValueError("Duplicate geo-year-series rows in the market extract")
    wide = long.pivot(index=["geo", "year"], columns="column", values="value").reset_index()
    # Codebook unit check: Germany, 2013.
    de = wide[(wide["geo"] == "DE") & (wide["year"] == 2013)].iloc[0]
    expected = {
        "e_cap_share": 67.0,
        "e_gen_share": 74.0,
        "e_cap_top": 29.0,
        "e_gen_top": 32.0,
        "gas_retailers": 825.0,
    }
    for column, target in expected.items():
        if float(de[column]) != target:
            raise AssertionError(f"Unit check failed for {column}: {de[column]} != {target}")
    return wide


def load_gas(refresh: bool) -> pd.DataFrame:
    cache = EXTERNAL / "gas_final_consumption.csv"
    if cache.exists() and not refresh:
        return pd.read_csv(cache)
    frames = []
    for code in ("FC_E", "FC_NE"):
        payload = fetch_jsonstat(
            "nrg_bal_s",
            {
                "freq": "A",
                "nrg_bal": code,
                "siec": "G3000",
                "unit": "GWH",
                "sinceTimePeriod": str(YEAR_MIN),
                "untilTimePeriod": str(YEAR_MAX),
            },
        )
        frame = jsonstat_frame(payload, "gwh")
        frame = frame.rename(columns={"gwh": f"{code.lower()}_gwh"})
        frames.append(frame[["geo", "time", f"{code.lower()}_gwh"]].rename(columns={"time": "year"}))
    gas = frames[0].merge(frames[1], on=["geo", "year"], how="outer")
    gas["year"] = gas["year"].astype(int)
    gas["gas_fc_gwh"] = gas["fc_e_gwh"] + gas["fc_ne_gwh"]
    both_missing = gas["fc_e_gwh"].isna() | gas["fc_ne_gwh"].isna()
    gas.loc[both_missing, "gas_fc_gwh"] = np.nan
    cache.parent.mkdir(parents=True, exist_ok=True)
    gas.to_csv(cache, index=False)
    return gas


def load_population(refresh: bool) -> pd.DataFrame:
    cache = EXTERNAL / "population_1january.csv"
    if cache.exists() and not refresh:
        pop = pd.read_csv(cache)
        _check_population(pop)
        return pop
    payload = fetch_jsonstat(
        "demo_pjan",
        {
            "freq": "A",
            "unit": "NR",
            "age": "TOTAL",
            "sex": "T",
            "sinceTimePeriod": str(YEAR_MIN),
            "untilTimePeriod": str(YEAR_MAX),
        },
    )
    pop = jsonstat_frame(payload, "pop")
    pop = pop.rename(columns={"time": "year"})
    pop["year"] = pop["year"].astype(int)
    pop = pop[["geo", "year", "pop"]]
    cache.parent.mkdir(parents=True, exist_ok=True)
    pop.to_csv(cache, index=False)
    _check_population(pop)
    return pop


def _check_population(pop: pd.DataFrame) -> None:
    de_2013 = pop[(pop["geo"] == "DE") & (pop["year"] == 2013)]["pop"]
    if de_2013.empty or int(de_2013.iloc[0]) != 80523746:
        raise AssertionError(f"Population unit check failed for Germany 2013: {de_2013.tolist()}")


def build_panel(market: pd.DataFrame, gas: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    panel = market.merge(gas, on=["geo", "year"], how="left")
    panel = panel.merge(pop, on=["geo", "year"], how="left")
    panel = panel[(panel["year"] >= YEAR_MIN) & (panel["year"] <= YEAR_MAX)].copy()
    panel["retailers_per_twh"] = panel["gas_retailers"] / (panel["gas_fc_gwh"] / 1000.0)
    panel["in_density_sample"] = (
        panel["gas_retailers"].notna()
        & panel["gas_fc_gwh"].notna()
        & (panel["gas_fc_gwh"] >= GAS_FLOOR_GWH)
    )
    panel["retailers_per_million"] = np.where(
        panel["in_density_sample"] & panel["pop"].notna() & (panel["pop"] > 0),
        panel["gas_retailers"] / (panel["pop"] / 1_000_000.0),
        np.nan,
    )
    de_2019 = panel[(panel["geo"] == "DE") & (panel["year"] == 2019)]["gas_fc_gwh"]
    if de_2019.empty or not (400_000 <= float(de_2019.iloc[0]) <= 1_200_000):
        raise AssertionError(
            f"Germany 2019 final gas consumption is outside 400–1,200 TWh in GWh: {de_2019.tolist()}"
        )
    return panel.sort_values(["geo", "year"]).reset_index(drop=True)


def yearly_distribution(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    for year, group in frame.dropna(subset=[column]).groupby("year"):
        values = group[column].astype(float)
        germany = group.loc[group["geo"] == "DE", column]
        de_value = float(germany.iloc[0]) if len(germany) else np.nan
        ranks = values.rank(ascending=False, method="min")
        de_rank = float(ranks[germany.index].iloc[0]) if len(germany) else np.nan
        rows.append(
            {
                "year": int(year),
                "de": de_value,
                "median": float(values.median()),
                "p25": float(values.quantile(0.25)),
                "p75": float(values.quantile(0.75)),
                "de_minus_median": de_value - float(values.median()) if pd.notna(de_value) else np.nan,
                "de_rank": de_rank,
                "n": int(values.shape[0]),
            }
        )
    return pd.DataFrame(rows).sort_values("year")


def share_direction(delta: float) -> str:
    if delta <= -SHARE_FLAT_PP:
        return "fell"
    if delta >= SHARE_FLAT_PP:
        return "rose"
    return "stayed within 2 percentage points"


def density_direction(old: float, new: float) -> str:
    if old == 0:
        return "rose" if new > 0 else "stayed within 10 percent of its 2013 level"
    change = (new - old) / abs(old)
    if change <= -DENSITY_FLAT_REL:
        return "fell"
    if change >= DENSITY_FLAT_REL:
        return "rose"
    return "stayed within 10 percent of its 2013 level"


def endpoint(table: pd.DataFrame, year: int, column: str) -> float:
    hit = table.loc[table["year"] == year, column]
    if hit.empty:
        raise ValueError(f"Missing {column} in {year}")
    return float(hit.iloc[0])


def plot_band(table: pd.DataFrame, ylabel: str, title: str, source: str, path: Path) -> None:
    years = table["year"].to_numpy()
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.fill_between(
        years,
        table["p25"],
        table["p75"],
        color="#d9d9d9",
        label="Interquartile range",
    )
    ax.plot(years, table["median"], color="#4d4d4d", linewidth=1.6, label="Median")
    ax.plot(years, table["de"], color="#0b3a66", linewidth=2.2, label="Germany")
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_xticks(years)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.20))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.28)
    fig.text(0.5, 0.02, source, ha="center", fontsize=8, color="#555555")
    fig.savefig(path, format="svg")
    fig.savefig(path.with_suffix(".png"), dpi=140)
    plt.close(fig)


def excluded_rows(panel: pd.DataFrame) -> pd.DataFrame:
    has_retailers = panel["gas_retailers"].notna()
    below = has_retailers & panel["gas_fc_gwh"].notna() & (panel["gas_fc_gwh"] < GAS_FLOOR_GWH)
    missing = has_retailers & panel["gas_fc_gwh"].isna()
    out = panel.loc[below | missing, ["geo", "year", "gas_retailers", "gas_fc_gwh"]].copy()
    out["reason"] = np.where(out["gas_fc_gwh"].isna(), "missing_final_consumption", "below_1_twh")
    return out.sort_values(["reason", "geo", "year"])


def fit_twoway(frame: pd.DataFrame, outcome: str) -> dict:
    d = frame.dropna(subset=[outcome, "e_gen_share", "geo", "year"]).copy()
    counts = d.groupby("geo").size()
    d = d[d["geo"].isin(counts[counts >= MIN_YEARS_FOR_FE].index)].copy()
    d = d.sort_values(["geo", "year"])
    if d["geo"].nunique() < 3 or d["year"].nunique() < 3:
        raise RuntimeError(f"Too few groups to fit two-way fixed effects for {outcome}")
    formula = f"{outcome} ~ e_gen_share + C(geo) + C(year)"
    fe_only = smf.ols(f"{outcome} ~ C(geo) + C(year)", data=d).fit()
    full = smf.ols(formula, data=d).fit(
        cov_type="cluster",
        cov_kwds={"groups": d["geo"]},
    )
    coef = float(full.params["e_gen_share"])
    se = float(full.bse["e_gen_share"])
    ci_low, ci_high = (float(x) for x in full.conf_int().loc["e_gen_share"])
    return {
        "outcome": outcome,
        "coef": coef,
        "se": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n_obs": int(full.nobs),
        "n_countries": int(d["geo"].nunique()),
        "n_years": int(d["year"].nunique()),
        "within_r2": float(1 - full.ssr / fe_only.ssr) if fe_only.ssr else np.nan,
        "sample": d,
        "dropped_singleton_countries": sorted(set(counts[counts < MIN_YEARS_FOR_FE].index)),
    }


def leave_one_out(sample: pd.DataFrame, outcome: str, baseline: float) -> pd.DataFrame:
    rows = []
    for geo in sorted(sample["geo"].unique()):
        held = sample[sample["geo"] != geo]
        try:
            fit = fit_twoway(held, outcome)
        except RuntimeError:
            continue
        coef = fit["coef"]
        rows.append(
            {
                "geo_dropped": geo,
                "coef": coef,
                "se": fit["se"],
                "n_obs": fit["n_obs"],
                "n_countries": fit["n_countries"],
                "same_sign": bool(np.sign(coef) == np.sign(baseline) and coef != 0 and baseline != 0),
                "rel_abs_diff": abs(coef - baseline) / abs(baseline) if baseline != 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def fmt(value: float, digits: int) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.{digits}f}"


def write_results(
    panel: pd.DataFrame,
    share_tables: dict[str, pd.DataFrame],
    density: pd.DataFrame,
    per_million: pd.DataFrame,
    excluded: pd.DataFrame,
    snapshot: pd.DataFrame,
    baseline: dict,
    sensitivity: dict,
    loo: pd.DataFrame,
    survives: bool,
) -> None:
    cap = share_tables["e_cap_share"]
    gen = share_tables["e_gen_share"]
    lines = [
        "# Pipeline results",
        "",
        "Generated by `scripts/run_pipeline.py`. Do not edit by hand.",
        "",
        "## Rules fixed before the ranks",
        "",
        "- Window: 2013–2023. Rank 1 is the highest value. Ties take the minimum rank.",
        "- The median and interquartile range include Germany and every other country with a non-missing value that year.",
        f"- A share “fell” or “rose” only if the 2013–2023 change exceeds {SHARE_FLAT_PP:.0f} percentage points. Otherwise it stayed within that band.",
        f"- Retailer density “fell” or “rose” only if the 2023 level is at least {DENSITY_FLAT_REL:.0%} away from 2013.",
        "- Density ranks use country-years with final gas consumption of at least 1 TWh.",
        f"- RQ3 enters the abstract only if every leave-one-out coefficient on retailer density has the same sign as the baseline and lies within {LOO_BAND:.0%} of it. The baseline is two-way fixed effects of retailers per TWh on the cumulative generation share, with standard errors clustered by country.",
        "",
        "## Sample",
        "",
        f"- Country-years in the window: {len(panel)}.",
        f"- Non-missing cumulative capacity share: {int(panel['e_cap_share'].notna().sum())}.",
        f"- Non-missing cumulative generation share: {int(panel['e_gen_share'].notna().sum())}.",
        f"- Non-missing gas-retailer counts: {int(panel['gas_retailers'].notna().sum())}.",
        f"- Density sample (count observed and final consumption at least 1 TWh): {int(panel['in_density_sample'].sum())}.",
        f"- Retailer counts excluded from the density ranking: {len(excluded)} "
        f"({int((excluded['reason']=='below_1_twh').sum())} below 1 TWh, "
        f"{int((excluded['reason']=='missing_final_consumption').sum())} missing consumption).",
        f"- RQ3 common sample: {baseline['n_obs']} country-years, {baseline['n_countries']} countries, {baseline['n_years']} years.",
        "",
        "## RQ1. Electricity concentration",
        "",
    ]
    for key, label in (
        ("e_cap_share", "Cumulative capacity share"),
        ("e_gen_share", "Cumulative generation share"),
        ("e_cap_top", "Largest-firm capacity share"),
        ("e_gen_top", "Largest-firm generation share"),
    ):
        table = share_tables[key]
        v0, v1 = endpoint(table, 2013, "de"), endpoint(table, 2023, "de")
        m0, m1 = endpoint(table, 2013, "median"), endpoint(table, 2023, "median")
        r0, r1 = endpoint(table, 2013, "de_rank"), endpoint(table, 2023, "de_rank")
        n0, n1 = int(endpoint(table, 2013, "n")), int(endpoint(table, 2023, "n"))
        g0, g1 = endpoint(table, 2013, "de_minus_median"), endpoint(table, 2023, "de_minus_median")
        lines.append(
            f"- {label}: Germany {share_direction(v1 - v0)} from {fmt(v0, 1)}% in 2013 to {fmt(v1, 1)}% in 2023 "
            f"({fmt(v1 - v0, 1)} percentage points). The cross-country median moved from {fmt(m0, 1)}% to {fmt(m1, 1)}%. "
            f"Germany was {fmt(g0, 1)} percentage points from the median in 2013 and {fmt(g1, 1)} in 2023 "
            f"(negative means below the median). Rank {r0:.0f} of {n0} in 2013 and {r1:.0f} of {n1} in 2023 "
            "(1 = highest share)."
        )
    lines += [
        "",
        "## RQ2. Gas retailers per TWh",
        "",
    ]
    v0, v1 = endpoint(density, 2013, "de"), endpoint(density, 2023, "de")
    m0, m1 = endpoint(density, 2013, "median"), endpoint(density, 2023, "median")
    r0, r1 = endpoint(density, 2013, "de_rank"), endpoint(density, 2023, "de_rank")
    n0, n1 = int(endpoint(density, 2013, "n")), int(endpoint(density, 2023, "n"))
    lines.append(
        f"- Germany’s retailer density {density_direction(v0, v1)}: {fmt(v0, 2)} retailers per TWh in 2013 and "
        f"{fmt(v1, 2)} in 2023. The median moved from {fmt(m0, 2)} to {fmt(m1, 2)}. "
        f"Rank {r0:.0f} of {n0} in 2013 and {r1:.0f} of {n1} in 2023 (1 = most retailers per TWh)."
    )
    if not per_million.empty and per_million["de"].notna().all():
        p0, p1 = endpoint(per_million, 2013, "de"), endpoint(per_million, 2023, "de")
        pr0, pr1 = endpoint(per_million, 2013, "de_rank"), endpoint(per_million, 2023, "de_rank")
        pn0, pn1 = int(endpoint(per_million, 2013, "n")), int(endpoint(per_million, 2023, "n"))
        lines.append(
            f"- Robustness, retailers per million inhabitants on the same 1 TWh screen: Germany {fmt(p0, 2)} in 2013 "
            f"(rank {pr0:.0f} of {pn0}) and {fmt(p1, 2)} in 2023 (rank {pr1:.0f} of {pn1}). "
            "Per person, Germany stays near the top. Per terawatt-hour, it does not. The headline rank is the per-terawatt-hour rank."
        )
    if not snapshot.empty:
        leaders = snapshot.nsmallest(3, "density_rank")
        bits = [
            f"{row.geo} ({row.gas_retailers:.0f} retailers, {row.gas_fc_gwh / 1000:.1f} TWh)"
            for row in leaders.itertuples(index=False)
        ]
        lines.append(
            "- The top of the 2023 density ranking is small markets just above the 1 TWh floor: "
            + "; ".join(bits)
            + ". Density removes the raw-count advantage of a large market, and it is noisy when the market is only a few terawatt-hours."
        )
    raw = panel[(panel["year"] == 2023) & panel["gas_retailers"].notna()].copy()
    raw["raw_rank"] = raw["gas_retailers"].rank(ascending=False, method="min")
    de_raw = raw.loc[raw["geo"] == "DE"]
    if len(de_raw):
        lines.append(
            f"- On the unscaled 2023 count, Germany ranks {float(de_raw['raw_rank'].iloc[0]):.0f} of {len(raw)} "
            f"with {float(de_raw['gas_retailers'].iloc[0]):.0f} retailers. That rank is market size. "
            f"The density rank above is the one the contract uses."
        )
    lines += [
        "",
        "## RQ3. Exploratory association",
        "",
        (
            f"- Baseline: a one-percentage-point higher cumulative generation share is associated with "
            f"{fmt(baseline['coef'], 3)} retailers per TWh "
            f"(cluster-robust 95% interval {fmt(baseline['ci_low'], 3)} to {fmt(baseline['ci_high'], 3)}; "
            f"within R² {fmt(baseline['within_r2'], 3)}; "
            f"{baseline['n_countries']} country clusters)."
        ),
        (
            f"- Same sample, unscaled retailer count as the outcome: coefficient {fmt(sensitivity['coef'], 3)} "
            f"(interval {fmt(sensitivity['ci_low'], 3)} to {fmt(sensitivity['ci_high'], 3)}). "
            "Country fixed effects remove permanent differences in market size, so this regression is not where the size confound shows up. The 2023 ranks are."
        ),
    ]
    n_same = int(loo["same_sign"].sum()) if len(loo) else 0
    crosses_zero = baseline["ci_low"] < 0 < baseline["ci_high"]
    zero_clause = (
        "The baseline interval includes zero and the within R² is about zero."
        if crosses_zero
        else "The within R² is the number reported above."
    )
    lines.append(
        f"- Leave-one-out coefficients range from {fmt(float(loo['coef'].min()), 3)} to {fmt(float(loo['coef'].max()), 3)}. "
        f"{n_same} of {len(loo)} keep the baseline sign, and "
        f"{int((loo['rel_abs_diff'] <= LOO_BAND).sum())} of {len(loo)} stay within 50% of it. "
        f"{zero_clause}"
    )
    if survives:
        lines.append(
            "- Abstract rule: the density coefficient keeps its sign and stays within 50% of the baseline "
            "in every leave-one-out. It is eligible for the abstract as an association, with the interval above."
        )
    else:
        lines.append(
            "- Abstract rule: the density coefficient does not keep both its sign and its rough magnitude "
            "across every leave-one-out. RQ3 stays out of the abstract."
        )
    if baseline["dropped_singleton_countries"]:
        dropped = ", ".join(baseline["dropped_singleton_countries"])
        lines.append(f"- Countries with fewer than two years in the RQ3 sample were left out of the regression: {dropped}.")
    lines += [
        "",
        "## Files",
        "",
        "- Panel: `data/analysis/country_year_panel.csv`",
        "- Tables: `output/tables/`",
        "- Figures: `output/figures/`",
        "",
    ]
    (ROOT / "output" / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-download Eurostat supplements")
    args = parser.parse_args()

    for folder in (EXTERNAL, ANALYSIS, TABLES, FIGURES):
        folder.mkdir(parents=True, exist_ok=True)

    market = load_market(TSV_PATH)
    gas = load_gas(args.refresh)
    pop = load_population(args.refresh)
    panel = build_panel(market, gas, pop)
    panel.to_csv(ANALYSIS / "country_year_panel.csv", index=False)

    share_tables = {}
    for column in SHARE_SERIES:
        table = yearly_distribution(panel, column)
        share_tables[column] = table
        table.to_csv(TABLES / f"table_rq1_{column}.csv", index=False)

    density_base = panel.loc[panel["in_density_sample"]].copy()
    density = yearly_distribution(density_base, "retailers_per_twh")
    density.to_csv(TABLES / "table_rq2_retailers_per_twh.csv", index=False)
    per_million = yearly_distribution(density_base.dropna(subset=["retailers_per_million"]), "retailers_per_million")
    per_million.to_csv(TABLES / "table_rq2_retailers_per_million.csv", index=False)

    excluded = excluded_rows(panel)
    excluded.to_csv(TABLES / "table_rq2_excluded.csv", index=False)

    snap = density_base[density_base["year"] == 2023][
        ["geo", "gas_retailers", "gas_fc_gwh", "retailers_per_twh", "retailers_per_million"]
    ].copy()
    snap["density_rank"] = snap["retailers_per_twh"].rank(ascending=False, method="min")
    snap["raw_rank"] = snap["gas_retailers"].rank(ascending=False, method="min")
    snap.sort_values("density_rank").to_csv(TABLES / "table_rq2_snapshot_2023.csv", index=False)

    source_market = "Source: Eurostat nrg_ind_market, 2013–2023. Band is the cross-country interquartile range."
    source_density = (
        "Source: Eurostat nrg_ind_market and nrg_bal_s (FC_E + FC_NE). "
        "Countries with final gas consumption of at least 1 TWh."
    )
    plot_band(
        share_tables["e_cap_share"],
        "Percent of national electricity capacity",
        "Germany and the European distribution: capacity share of firms with at least 5%",
        source_market,
        FIGURES / "fig_rq1_capacity_share.svg",
    )
    plot_band(
        share_tables["e_gen_share"],
        "Percent of national electricity generation",
        "Germany and the European distribution: generation share of firms with at least 5%",
        source_market,
        FIGURES / "fig_rq1_generation_share.svg",
    )
    plot_band(
        density,
        "Gas retailers per TWh of final consumption",
        "Germany and the European distribution: gas-retailer density",
        source_density,
        FIGURES / "fig_rq2_retailer_density.svg",
    )

    baseline = fit_twoway(density_base, "retailers_per_twh")
    sensitivity = fit_twoway(density_base, "gas_retailers")
    loo = leave_one_out(baseline["sample"], "retailers_per_twh", baseline["coef"])
    loo.to_csv(TABLES / "table_rq3_leave_one_out.csv", index=False)
    survives = bool(len(loo) and loo["same_sign"].all() and (loo["rel_abs_diff"] <= LOO_BAND).all())
    pd.DataFrame(
        [
            {
                "spec": "density_twoway_fe",
                "outcome": "retailers_per_twh",
                "coef_per_pp": baseline["coef"],
                "se": baseline["se"],
                "ci_low": baseline["ci_low"],
                "ci_high": baseline["ci_high"],
                "within_r2": baseline["within_r2"],
                "n_obs": baseline["n_obs"],
                "n_countries": baseline["n_countries"],
                "abstract_rule_met": survives,
            },
            {
                "spec": "raw_count_same_sample",
                "outcome": "gas_retailers",
                "coef_per_pp": sensitivity["coef"],
                "se": sensitivity["se"],
                "ci_low": sensitivity["ci_low"],
                "ci_high": sensitivity["ci_high"],
                "within_r2": sensitivity["within_r2"],
                "n_obs": sensitivity["n_obs"],
                "n_countries": sensitivity["n_countries"],
                "abstract_rule_met": False,
            },
        ]
    ).to_csv(TABLES / "table_rq3_estimates.csv", index=False)

    rq3_countries = set(baseline["sample"]["geo"])
    descriptive_gen = set(panel.loc[panel["e_gen_share"].notna(), "geo"])
    flow = pd.DataFrame(
        [
            {"item": "countries_with_generation_share", "n": len(descriptive_gen)},
            {"item": "countries_in_rq3", "n": len(rq3_countries)},
            {"item": "countries_in_generation_not_in_rq3", "n": len(descriptive_gen - rq3_countries)},
            {"item": "rq3_country_years", "n": baseline["n_obs"]},
            {"item": "density_country_years", "n": int(panel["in_density_sample"].sum())},
        ]
    )
    flow.to_csv(TABLES / "table_sample_flow.csv", index=False)

    write_results(
        panel, share_tables, density, per_million, excluded, snap, baseline, sensitivity, loo, survives
    )
    print(f"Panel rows: {len(panel)}")
    print(f"RQ3 coefficient: {baseline['coef']:.4f} [{baseline['ci_low']:.4f}, {baseline['ci_high']:.4f}]")
    print(f"Abstract rule met: {survives}")
    print(f"Wrote {ROOT / 'output' / 'RESULTS.md'}")


if __name__ == "__main__":
    main()

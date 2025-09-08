import csv
from pathlib import Path
from collections import defaultdict

# Selected indicators to keep as example features
KEEP_INDICATORS = {
    # Energy cost/access proxies (percent or levels)
    'CMPY_ECAP5',  # Electricity price competitiveness (proxy)
    'CMPY_EG5',    # Gas price competitiveness (proxy)
    'LCMPY_IECAP', # Low-carbon electricity indicator (proxy)
    'GRTL',        # Grid-related outages (proxy reliability)
}


def read_long(path: Path):
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def build_master(long_csv: Path, out_csv: Path):
    # Structure: key (geo, year) -> features dict
    features = defaultdict(dict)
    meta_store = {}

    for row in read_long(long_csv):
        geo = row['geo']
        year = row['year']
        indic = row['indic_nrgm']
        unit = row['unit']
        val = row['value']
        if indic not in KEEP_INDICATORS:
            continue
        key = (geo, year)
        col = f'{indic}_{unit}'
        features[key][col] = val
        meta_store[key] = {'geo': geo, 'year': year}

    # Derived indicators: example ratios if components exist
    rows = []
    for key, cols in features.items():
        base = meta_store[key].copy()
        # Convert numeric where possible
        numeric = {}
        for k, v in cols.items():
            try:
                numeric[k] = float(v) if v != '' else None
            except Exception:
                numeric[k] = None
        # Example derived: energy_price_gap = CMPY_ECAP5_PC - CMPY_EG5_PC
        ecap = numeric.get('CMPY_ECAP5_PC')
        eg = numeric.get('CMPY_EG5_PC')
        if ecap is not None and eg is not None:
            cols['DERIV_energy_price_gap_PC'] = f"{ecap - eg:.3f}"
        else:
            cols['DERIV_energy_price_gap_PC'] = ''

        # Attach cols
        base.update({k: (v if isinstance(v, str) else ('' if v is None else str(v))) for k, v in cols.items()})
        rows.append(base)

    # Determine columns
    colnames = ['geo', 'year']
    all_cols = set()
    for r in rows:
        all_cols.update(r.keys())
    for c in sorted(all_cols):
        if c not in colnames:
            colnames.append(c)

    with out_csv.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=colnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    long_csv = root / 'data' / 'estat_nrg_ind_market_long.csv'
    out_csv = root / 'data' / 'master_dataset.csv'
    build_master(long_csv, out_csv)
    print(f'Wrote master dataset to: {out_csv}')

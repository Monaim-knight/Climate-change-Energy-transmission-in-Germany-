import csv
from pathlib import Path
from collections import defaultdict


def read_csv(path: Path):
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False


def profile_long(path: Path):
    total = 0
    missing = 0
    min_val = None
    max_val = None
    units = set()
    geos = set()
    indicators = set()
    for row in read_csv(path):
        total += 1
        geos.add(row.get('geo', ''))
        units.add(row.get('unit', ''))
        indicators.add(row.get('indic_nrgm', ''))
        v = row.get('value', '')
        if v == '' or v is None:
            missing += 1
        elif is_number(v):
            x = float(v)
            min_val = x if min_val is None else min(min_val, x)
            max_val = x if max_val is None else max(max_val, x)
    return {
        'rows': total,
        'missing_values': missing,
        'min_value': min_val,
        'max_value': max_val,
        'unique_units': len(units),
        'unique_geos': len(geos),
        'unique_indicators': len(indicators),
    }


def profile_wide(path: Path):
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        meta_cols = ['freq', 'siec', 'indic_nrgm', 'unit', 'geo']
        year_cols = [c for c in fieldnames if c not in meta_cols]
        rows = list(reader)

    totals = {c: 0 for c in year_cols}
    missing = {c: 0 for c in year_cols}
    min_vals = {c: None for c in year_cols}
    max_vals = {c: None for c in year_cols}

    for row in rows:
        for c in year_cols:
            v = row.get(c, '')
            totals[c] += 1
            if v == '' or v is None:
                missing[c] += 1
            elif is_number(v):
                x = float(v)
                min_vals[c] = x if min_vals[c] is None else min(min_vals[c], x)
                max_vals[c] = x if max_vals[c] is None else max(max_vals[c], x)

    return {
        'rows': len(rows),
        'columns': len(fieldnames),
        'years': year_cols,
        'missing_by_year': missing,
        'min_by_year': min_vals,
        'max_by_year': max_vals,
    }


def main():
    root = Path(__file__).resolve().parents[1] / 'data'
    long_path = root / 'estat_nrg_ind_market_long.csv'
    wide_path = root / 'estat_nrg_ind_market_wide.csv'

    long_report = profile_long(long_path)
    wide_report = profile_wide(wide_path)

    print('Long format profile:')
    print(long_report)
    print('\nWide format profile:')
    print({k: (v if k in ['rows','columns','years'] else None) for k, v in wide_report.items()})
    print('\nMissing by year (wide):')
    print(wide_report['missing_by_year'])


if __name__ == '__main__':
    main()

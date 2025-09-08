import csv
from pathlib import Path

def parse_value(raw: str):
    s = raw.strip()
    if s == ':' or s == '':
        return ''
    # Remove spaces used as padding
    s = s.replace(' ', '')
    # Keep as-is (decimal dot). Return string to avoid locale issues
    return s


def clean_eurostat_tsv(tsv_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    with tsv_path.open('r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    if not lines:
        raise ValueError('Input file is empty')

    # Header: first token contains comma-separated meta header ending with geo\TIME_PERIOD
    # Remaining tokens are years separated by tabs
    header_parts = lines[0].split('\t')
    meta_header = header_parts[0]
    years = [h.strip() for h in header_parts[1:] if h.strip()]

    # Parse meta header columns (split on commas, last part contains geo\TIME_PERIOD -> keep as 'geo')
    meta_cols = [h.strip() for h in meta_header.split(',')]
    # Fix last meta column name if it contains geo\TIME_PERIOD
    if meta_cols and meta_cols[-1].startswith('geo'):
        meta_cols[-1] = 'geo'

    required_meta_cols = ['freq', 'siec', 'indic_nrgm', 'unit', 'geo']
    # If names don't match, still force to expected names
    if len(meta_cols) != 5:
        meta_cols = required_meta_cols

    rows_wide = []
    rows_long = []

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split('\t')
        meta = parts[0]
        values = parts[1:]

        meta_vals = [m.strip() for m in meta.split(',')]
        if len(meta_vals) != 5:
            # Skip malformed rows
            continue
        record = dict(zip(required_meta_cols, meta_vals))

        # Build wide row
        wide_row = {**record}
        for idx, year in enumerate(years):
            val = parse_value(values[idx]) if idx < len(values) else ''
            wide_row[year] = val
            if val != '':
                rows_long.append({**record, 'year': year, 'value': val})
            else:
                # Keep explicit missing as empty in long as well
                rows_long.append({**record, 'year': year, 'value': ''})
        rows_wide.append(wide_row)

    # Write wide CSV
    wide_cols = required_meta_cols + years
    wide_csv = out_dir / 'estat_nrg_ind_market_wide.csv'
    with wide_csv.open('w', encoding='utf-8', newline='') as wf:
        writer = csv.DictWriter(wf, fieldnames=wide_cols)
        writer.writeheader()
        for r in rows_wide:
            writer.writerow(r)

    # Write long CSV
    long_cols = required_meta_cols + ['year', 'value']
    long_csv = out_dir / 'estat_nrg_ind_market_long.csv'
    with long_csv.open('w', encoding='utf-8', newline='') as lf:
        writer = csv.DictWriter(lf, fieldnames=long_cols)
        writer.writeheader()
        for r in rows_long:
            writer.writerow(r)

    return str(wide_csv), str(long_csv)


if __name__ == '__main__':
    project_root = Path(__file__).resolve().parents[1]
    tsv_file = project_root / 'estat_nrg_ind_market.tsv'
    out_directory = project_root / 'data'
    wide_path, long_path = clean_eurostat_tsv(tsv_file, out_directory)
    print(f'Wrote wide CSV to: {wide_path}')
    print(f'Wrote long CSV to: {long_path}')

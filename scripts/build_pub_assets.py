import csv
import os
from pathlib import Path
from collections import defaultdict
import statistics


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
MASTER = DATA_DIR / 'master_dataset.csv'
OUT_DIR = ROOT / 'paper' / 'assets'
TABLES_DIR = ROOT / 'paper' / 'tables'


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_master():
    rows = []
    with open(MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def to_float(value):
    try:
        if value is None or value == '':
            return None
        return float(value)
    except Exception:
        return None


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')


def scale(value, vmin, vmax, out_min, out_max):
    if value is None:
        return None
    if vmax == vmin:
        return (out_min + out_max) / 2
    ratio = (value - vmin) / (vmax - vmin)
    return out_min + ratio * (out_max - out_min)


def svg_header(width, height):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .axis {{ stroke:#333; stroke-width:1; fill:none; }}
  .grid {{ stroke:#ddd; stroke-width:1; fill:none; }}
  .label {{ font-family: Arial, sans-serif; font-size:12px; fill:#111; }}
  .title {{ font-family: Arial, sans-serif; font-size:16px; font-weight:bold; fill:#111; }}
  .tick {{ font-family: Arial, sans-serif; font-size:10px; fill:#333; }}
  .bar {{ fill:#4C78A8; }}
  .line {{ stroke:#E45756; stroke-width:2; fill:none; }}
  .cell {{ stroke:#fff; stroke-width:1; }}
  .legend {{ font-family: Arial, sans-serif; font-size:11px; fill:#111; }}
  .note {{ font-family: Arial, sans-serif; font-size:10px; fill:#666; }}
  .country {{ font-family: Arial, sans-serif; font-size:9px; fill:#111; }}
</style>
"""


def svg_footer():
    return "</svg>\n"


def color_scale_blue(value, vmin, vmax):
    # simple light-to-dark blue
    if value is None:
        return '#cccccc'
    if vmax == vmin:
        t = 0.5
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    b = int(120 + 135 * t)   # 120..255
    g = int(150 + 60 * t)    # 150..210
    r = int(76)              # fixed
    return f"#{r:02x}{g:02x}{b:02x}"


def figure_de_timeseries(rows):
    # Germany time-series for GRTL_NR
    series = [(int(r['year']), to_float(r.get('GRTL_NR'))) for r in rows if r.get('geo') == 'DE' and r.get('year')]
    series = [(y, v) for y, v in series if v is not None]
    series.sort(key=lambda x: x[0])
    if not series:
        return

    width, height = 720, 360
    margin = 60
    x0, y0 = margin, height - margin
    x1, y1 = width - margin, margin

    years = [y for y, _ in series]
    vals = [v for _, v in series]
    vmin, vmax = min(vals), max(vals)
    xmin, xmax = min(years), max(years)

    # Build path
    pts = []
    for y, v in series:
        x = scale(y, xmin, xmax, x0, x1)
        yy = scale(v, vmin, vmax, y0, y1)
        pts.append((x, yy))

    path_d = 'M ' + ' L '.join(f"{x:.1f} {yy:.1f}" for x, yy in pts)

    svg = []
    svg.append(svg_header(width, height))
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#ffffff' />")
    # axes
    svg.append(f"<line class='axis' x1='{x0}' y1='{y0}' x2='{x1}' y2='{y0}' />")
    svg.append(f"<line class='axis' x1='{x0}' y1='{y0}' x2='{x0}' y2='{y1}' />")
    # grid and ticks
    for i, y in enumerate(years):
        if i % 2 == 0:
            xx = scale(y, xmin, xmax, x0, x1)
            svg.append(f"<line class='grid' x1='{xx}' y1='{y0}' x2='{xx}' y2='{y1}' />")
            svg.append(f"<text class='tick' x='{xx}' y='{y0+14}' text-anchor='middle'>{y}</text>")
    for t in range(5):
        val = vmin + t*(vmax-vmin)/4 if vmax>vmin else vmin
        yy = scale(val, vmin, vmax, y0, y1)
        svg.append(f"<line class='grid' x1='{x0}' y1='{yy}' x2='{x1}' y2='{yy}' />")
        svg.append(f"<text class='tick' x='{x0-6}' y='{yy+4}' text-anchor='end'>{val:.0f}</text>")
    svg.append(f"<path class='line' d='{path_d}' />")
    svg.append(f"<text class='title' x='{width/2}' y='24' text-anchor='middle'>Germany GRTL_NR over time</text>")
    svg.append(svg_footer())
    write_file(OUT_DIR / 'fig_de_grtl_timeseries.svg', ''.join(svg))


def figure_top_countries_bar(rows):
    # mean GRTL_NR by country, top 10
    grp = defaultdict(list)
    for r in rows:
        g = r.get('geo')
        v = to_float(r.get('GRTL_NR'))
        if g and v is not None:
            grp[g].append(v)
    stats = []
    for g, arr in grp.items():
        if len(arr) >= 5:
            stats.append((g, statistics.mean(arr)))
    stats.sort(key=lambda x: x[1], reverse=True)
    stats = stats[:10]
    if not stats:
        return

    width, height = 720, 420
    margin = 80
    x0, y0 = margin, height - margin
    x1, y1 = width - margin, margin
    vmin, vmax = 0, max(v for _, v in stats)
    bar_w = (x1 - x0) / len(stats) * 0.6

    svg = []
    svg.append(svg_header(width, height))
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#ffffff' />")
    svg.append(f"<line class='axis' x1='{x0}' y1='{y0}' x2='{x1}' y2='{y0}' />")
    svg.append(f"<line class='axis' x1='{x0}' y1='{y0}' x2='{x0}' y2='{y1}' />")
    # y ticks
    for t in range(5):
        val = vmin + t*(vmax-vmin)/4 if vmax>vmin else vmin
        yy = scale(val, vmin, vmax, y0, y1)
        svg.append(f"<line class='grid' x1='{x0}' y1='{yy}' x2='{x1}' y2='{yy}' />")
        svg.append(f"<text class='tick' x='{x0-6}' y='{yy+4}' text-anchor='end'>{val:.0f}</text>")

    for i, (g, v) in enumerate(stats):
        cx = x0 + (i+0.5)*(x1-x0)/len(stats)
        yy = scale(v, vmin, vmax, y0, y1)
        svg.append(f"<rect class='bar' x='{cx - bar_w/2:.1f}' y='{yy:.1f}' width='{bar_w:.1f}' height='{(y0-yy):.1f}' />")
        svg.append(f"<text class='tick' x='{cx:.1f}' y='{y0+14}' text-anchor='middle'>{g}</text>")
        svg.append(f"<text class='tick' x='{cx:.1f}' y='{yy-6:.1f}' text-anchor='middle'>{v:.1f}</text>")

    svg.append(f"<text class='title' x='{width/2}' y='24' text-anchor='middle'>Top countries by mean GRTL_NR</text>")
    svg.append(svg_footer())
    write_file(OUT_DIR / 'fig_top_countries_grtl.svg', ''.join(svg))


def figure_correlation_heatmap(rows):
    # compute correlations among 4 variables
    vars_ = ['CMPY_ECAP5_PC', 'CMPY_EG5_PC', 'DERIV_energy_price_gap_PC', 'GRTL_NR']
    data = {k: [] for k in vars_}
    # collect only complete rows for these vars
    for r in rows:
        vals = [to_float(r.get(k)) for k in vars_]
        if all(v is not None for v in vals):
            for k, v in zip(vars_, vals):
                data[k].append(v)

    def corr(a, b):
        n = len(a)
        if n < 2:
            return 0.0
        ma = statistics.mean(a)
        mb = statistics.mean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return (num / den) if den else 0.0

    M = [[0.0 for _ in vars_] for _ in vars_]
    for i, vi in enumerate(vars_):
        for j, vj in enumerate(vars_):
            M[i][j] = corr(data[vi], data[vj]) if data[vi] and data[vj] else 0.0

    # render heatmap
    width, height = 480, 480
    margin = 100
    x0, y0 = margin, margin
    size = min(width - margin*2, height - margin*2)
    cell = size / len(vars_)
    svg = []
    svg.append(svg_header(width, height))
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#ffffff' />")
    for i in range(len(vars_)):
        for j in range(len(vars_)):
            v = M[i][j]
            # map -1..1 to red..blue
            t = max(-1.0, min(1.0, v))
            # red to blue gradient
            r = int(230 * (t < 0) * (-t) + 30)
            b = int(230 * (t > 0) * (t) + 30)
            g = 60
            color = f"#{r:02x}{g:02x}{b:02x}"
            x = x0 + j * cell
            y = y0 + i * cell
            svg.append(f"<rect class='cell' x='{x:.1f}' y='{y:.1f}' width='{cell:.1f}' height='{cell:.1f}' fill='{color}' />")
            svg.append(f"<text class='label' x='{x + cell/2:.1f}' y='{y + cell/2 + 4:.1f}' text-anchor='middle' fill='#fff'>{v:.2f}</text>")
    for i, name in enumerate(vars_):
        svg.append(f"<text class='label' x='{x0 - 10}' y='{y0 + i*cell + cell/2 + 4}' text-anchor='end'>{name}</text>")
        svg.append(f"<text class='label' x='{x0 + i*cell + cell/2}' y='{y0 - 10}' text-anchor='middle'>{name}</text>")
    svg.append(f"<text class='title' x='{width/2}' y='24' text-anchor='middle'>Correlation Heatmap</text>")
    svg.append(svg_footer())
    write_file(OUT_DIR / 'fig_correlation_heatmap.svg', ''.join(svg))


def figure_tile_grid_map(rows):
    # Tile grid map: place country codes on a fixed grid; color by mean GRTL_NR
    # Simple grid layout by rough region blocks
    layout = [
        ['IS','NO','SE','FI'],
        ['IE','UK','DK','EE','LV','LT'],
        ['PT','ES','FR','BE','NL','DE','PL','CZ'],
        ['IT','AT','CH','SI','HR','HU','SK'],
        ['BA','RS','RO','BG','GR','TR'],
        ['AL','MK','XK','ME','MD','UA'],
        ['MT','CY']
    ]
    # collect means
    grp = defaultdict(list)
    for r in rows:
        g = r.get('geo')
        v = to_float(r.get('GRTL_NR'))
        if g and v is not None:
            grp[g].append(v)
    means = {g: (sum(vs)/len(vs) if vs else None) for g, vs in grp.items()}
    vals = [v for v in means.values() if v is not None]
    if not vals:
        return
    vmin, vmax = min(vals), max(vals)

    width, height = 800, 480
    margin = 40
    cell = 52
    svg = []
    svg.append(svg_header(width, height))
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#ffffff' />")

    y = margin
    for row in layout:
        x = margin
        for code in row:
            val = means.get(code)
            fill = color_scale_blue(val, vmin, vmax)
            svg.append(f"<rect x='{x}' y='{y}' width='{cell}' height='{cell}' fill='{fill}' stroke='#ffffff' />")
            svg.append(f"<text class='country' x='{x + cell/2}' y='{y + cell/2 + 3}' text-anchor='middle'>{code}</text>")
            x += cell + 6
        y += cell + 6

    # legend
    lx, ly = width - 220, margin
    svg.append(f"<text class='legend' x='{lx}' y='{ly-8}'>Mean GRTL_NR</text>")
    for i in range(10):
        t = i / 9 if 9 else 0
        val = vmin + t*(vmax-vmin)
        fill = color_scale_blue(val, vmin, vmax)
        svg.append(f"<rect x='{lx}' y='{ly + i*16}' width='18' height='14' fill='{fill}' stroke='#fff' />")
        svg.append(f"<text class='tick' x='{lx + 24}' y='{ly + i*16 + 12}'>{val:.0f}</text>")

    svg.append(f"<text class='title' x='{width/2}' y='24' text-anchor='middle'>Tile Grid Map: Mean GRTL_NR by Country</text>")
    svg.append(svg_footer())
    write_file(OUT_DIR / 'fig_tile_grid_map_grtl.svg', ''.join(svg))


def latex_table_descriptives(rows):
    vars_ = ['CMPY_ECAP5_PC', 'CMPY_EG5_PC', 'DERIV_energy_price_gap_PC', 'GRTL_NR']
    stats = []
    for var in vars_:
        vals = [to_float(r.get(var)) for r in rows]
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        stats.append((var, len(vals), statistics.mean(vals), statistics.stdev(vals) if len(vals)>1 else 0.0, min(vals), max(vals)))
    lines = [
        '\\begin{table}[ht]','\\centering','\\caption{Descriptive statistics}','\\label{tab:descriptives}',
        '\\begin{tabular}{lrrrrr}','\\hline','Variable & N & Mean & SD & Min & Max \\','\\hline'
    ]
    for var, n, mean, sd, mn, mx in stats:
        lines.append(f"{var} & {n} & {mean:.2f} & {sd:.2f} & {mn:.2f} & {mx:.2f} \\ ")
    lines += ['\\hline','\\end{tabular}','\\end{table}','']
    write_file(TABLES_DIR / 'table_descriptives.tex', '\n'.join(lines))


def latex_table_correlations(rows):
    vars_ = ['CMPY_ECAP5_PC', 'CMPY_EG5_PC', 'DERIV_energy_price_gap_PC', 'GRTL_NR']
    data = {k: [] for k in vars_}
    for r in rows:
        vals = [to_float(r.get(k)) for k in vars_]
        if all(v is not None for v in vals):
            for k, v in zip(vars_, vals):
                data[k].append(v)
    def corr(a, b):
        n = len(a)
        if n < 2:
            return 0.0
        ma = statistics.mean(a)
        mb = statistics.mean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return (num / den) if den else 0.0
    M = [[0.0 for _ in vars_] for _ in vars_]
    for i, vi in enumerate(vars_):
        for j, vj in enumerate(vars_):
            M[i][j] = corr(data[vi], data[vj]) if data[vi] and data[vj] else 0.0
    cols = 'l' + 'r'*len(vars_)
    lines = [
        '\\begin{table}[ht]','\\centering','\\caption{Correlation matrix}','\\label{tab:corr}',
        f'\\begin{{tabular}}{{{cols}}}','\\hline',' & ' + ' & '.join(vars_) + ' \\','\\hline'
    ]
    for i, vi in enumerate(vars_):
        row = [vi] + [f"{M[i][j]:.2f}" for j in range(len(vars_))]
        lines.append(' & '.join(row) + ' \\ ')
    lines += ['\\hline','\\end{tabular}','\\end{table}','']
    write_file(TABLES_DIR / 'table_correlations.tex', '\n'.join(lines))


def latex_table_regressions(rows):
    # simple bivariate OLS lines y = a + b x
    def fit(x, y):
        n = len(x)
        if n < 2:
            return (0.0, 0.0, 0.0)
        mx, my = statistics.mean(x), statistics.mean(y)
        num = sum((xi-mx)*(yi-my) for xi, yi in zip(x, y))
        den = sum((xi-mx)**2 for xi in x)
        b = (num/den) if den else 0.0
        a = my - b*mx
        yhat = [a + b*xi for xi in x]
        ss_res = sum((yi - yhi)**2 for yi, yhi in zip(y, yhat))
        ss_tot = sum((yi - my)**2 for yi in y)
        r2 = 1 - ss_res/ss_tot if ss_tot else 0.0
        return (a, b, r2)
    y = []
    x_ecap, x_eg, x_gap = [], [], []
    for r in rows:
        yy = to_float(r.get('GRTL_NR'))
        ecap = to_float(r.get('CMPY_ECAP5_PC'))
        eg = to_float(r.get('CMPY_EG5_PC'))
        gap = to_float(r.get('DERIV_energy_price_gap_PC'))
        if yy is not None:
            y.append(yy)
            x_ecap.append(ecap)
            x_eg.append(eg)
            x_gap.append(gap)
    # align complete cases
    pairs = []
    for xe, xg, xgap, yy in zip(x_ecap, x_eg, x_gap, y):
        if xe is not None and yy is not None:
            pairs.append(('ECAP', xe, yy))
        if xg is not None and yy is not None:
            pairs.append(('EG', xg, yy))
        if xgap is not None and yy is not None:
            pairs.append(('GAP', xgap, yy))
    # collect by model label
    by = defaultdict(lambda: ([], []))
    for label, xx, yy in pairs:
        by[label][0].append(xx)
        by[label][1].append(yy)
    rows_out = []
    labels = {'ECAP':'CMPY_ECAP5_PC','EG':'CMPY_EG5_PC','GAP':'DERIV_energy_price_gap_PC'}
    for label, (xxs, yys) in by.items():
        a, b, r2 = fit(xxs, yys)
        rows_out.append((labels[label], a, b, r2, len(xxs)))
    lines = [
        '\\begin{table}[ht]','\\centering','\\caption{Bivariate regressions: GRTL\\_NR on price indicators}','\\label{tab:reg_bivar}',
        '\\begin{tabular}{lrrrr}','\\hline','Model & Intercept & Slope & $R^2$ & N \\','\\hline'
    ]
    for name, a, b, r2, n in rows_out:
        lines.append(f"GRTL\\_NR ~ {name} & {a:.2f} & {b:.2f} & {r2:.3f} & {n} \\ ")
    lines += ['\\hline','\\end{tabular}','\\end{table}','']
    write_file(TABLES_DIR / 'table_regressions.tex', '\n'.join(lines))


def main():
    ensure_dirs()
    rows = load_master()
    if not rows:
        print('No data found at', MASTER)
        return
    # Figures
    figure_de_timeseries(rows)
    figure_top_countries_bar(rows)
    figure_correlation_heatmap(rows)
    figure_tile_grid_map(rows)
    # Tables
    latex_table_descriptives(rows)
    latex_table_correlations(rows)
    latex_table_regressions(rows)
    print('Publication assets generated in:', OUT_DIR)
    print('LaTeX tables generated in:', TABLES_DIR)


if __name__ == '__main__':
    main()




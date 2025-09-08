## Bridging Divides: Social Cohesion in the Face of Climate Change and Energy Transition in Germany

This repository contains the full research workflow, analysis scripts, data artifacts, figures, and manuscript for the project examining how European energy transition indicators relate to social cohesion-relevant structures, with a focus on Germany.

### Repository Structure

- `paper/` – manuscript sources and assets (LaTeX, Markdown, references, figures)
- `scripts/` – data processing and analysis scripts (Python)
- `data/` – input and generated datasets and analysis reports
- Project-phase documents – literature review, proposal, methodology notes, policy recommendations

---

### Data Collection and Preparation

- **Primary Source**: Eurostat energy market indicators `estat_nrg_ind_market` (35 European countries, 2013–2024)
- **Key Variables**:
  - `CMPY_ECAP5_PC`: Electricity price competitiveness (% of EU average)
  - `CMPY_EG5_PC`: Gas price competitiveness (% of EU average)
  - `GRTL_NR`: Grid-related infrastructure indicator
  - `DERIV_energy_price_gap_PC`: Derived energy price gap (electricity vs gas)

- **Collection & Cleaning**:
  - Downloaded TSV from Eurostat and converted to CSV with standardized headers
  - Geographic harmonization via NUTS (country level)
  - Temporal harmonization to annual frequency (2013–2024)
  - Missing value assessment and treatment
  - Constructed derived indicators

- **Documentation**:
  - `DATA_INVENTORY.md` – datasets, fields, and provenance
  - `HARMONIZATION_KEYS.md` – naming and transformation keys
  - `DATA_PREP_DOCUMENTATION.md` – cleaning pipeline

---

### Analysis Steps

All scripts live in `scripts/`. They are written to run with standard Python. Some outputs are also pre-generated in `data/analysis_results/`.

- `clean_eurostat_tsv.py` – parse TSV → CSV, normalize headers and types
- `build_master_dataset.py` – merge, harmonize geography/time, construct derived indicators → `data/master_dataset.csv`
- `descriptive_analysis.py` – descriptive stats → `data/analysis_results/simple_analysis_report.md`
- `correlation` and `regression`:
  - `simple_analysis.py` / `regression_analysis.py` – correlations and bivariate OLS → `data/analysis_results/regression_analysis_report.md`
- `visualization_analysis.py` – figures (SVG):
  - `paper/assets/fig_correlation_heatmap.svg`
  - `paper/assets/fig_de_grtl_timeseries.svg`
  - `paper/assets/fig_tile_grid_map_grtl.svg`
  - `paper/assets/fig_top_countries_grtl.svg`

Key findings (see manuscript for details):

- Strong market integration: electricity–gas price competitiveness correlation ≈ 0.893
- Germany leads grid infrastructure (`GRTL_NR` ≈ 953.5); notable regional disparities
- Temporal stability and policy effectiveness signals (2013–2024)

---

### Outputs

- Manuscript (Markdown): `paper/Research_Paper_Word_Version.md`
- LaTeX version and tables: `paper/main.tex`, `paper/tables/`
- Figures (SVG): `paper/assets/`
- Analysis reports: `data/analysis_results/`
- PDF-ready HTML (auto-generated): `Research_Paper_For_PDF.html`

Optional helpers in project root:

- `direct_pdf_converter.py` – generate print-optimized HTML and text versions from the manuscript
- `convert_paper_to_pdf.py` – WeasyPrint-based PDF conversion (requires conda env)
- `infographic.html` – visually summarized findings (interactive infographic)

---

### Reproducibility

Using Miniforge/conda (recommended):

```bash
cd "C:/Users/monai/OneDrive - student.uni-halle.de/Desktop/Research Assistant"

# Optional: create environment
conda create -n energy-paper -c conda-forge python=3.11 weasyprint markdown pygments cffi pango -y
conda activate energy-paper

# Regenerate PDF (WeasyPrint-based)
python convert_paper_to_pdf.py

# Or generate print-optimized HTML (no extra deps)
python direct_pdf_converter.py
```

To rerun data preparation and analysis (examples):

```bash
python scripts/clean_eurostat_tsv.py
python scripts/build_master_dataset.py
python scripts/descriptive_analysis.py
python scripts/regression_analysis.py
python scripts/visualization_analysis.py
```

---

### Recommendations for Future Research

- Integrate direct social cohesion indicators (e.g., trust, participation, inequality)
- Include controls (GDP, population density, political variables) and heterogeneity analysis
- Employ causal identification (IVs, natural experiments, policy discontinuities)
- Extend beyond Europe to compare global energy transition patterns
- Explore distributional impacts (energy justice) across regions and demographics

---

### Challenges Faced

- Environment constraints prevented use of some data science stacks initially (e.g., pandas),
  prompting standard-library implementations for stats and plotting fallbacks
- Missing values and inconsistent metadata across years required careful harmonization
- Maintaining comparability of indicators (definitions and base years) across countries
- Balancing publication-quality figures (SVG) with fully reproducible pipelines

---

### How to Cite / Acknowledge

Please cite the manuscript in `paper/` and the Eurostat `estat_nrg_ind_market` dataset when reusing data or code.

---

### License

Specify your preferred license here (e.g., MIT). If omitted, all rights reserved by default.



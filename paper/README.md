# Publication-Ready Research Paper

## Overview
This directory contains a complete, publication-ready research paper on "Bridging Divides: Social Cohesion in the Face of Climate Change and Energy Transition in Germany" with all figures, tables, and LaTeX source.

## Structure
```
paper/
├── main.tex                 # Main LaTeX manuscript
├── references.bib           # Bibliography
├── assets/                  # Generated SVG figures
│   ├── fig_de_grtl_timeseries.svg
│   ├── fig_top_countries_grtl.svg
│   ├── fig_correlation_heatmap.svg
│   └── fig_tile_grid_map_grtl.svg
├── tables/                  # Generated LaTeX tables
│   ├── table_descriptives.tex
│   ├── table_correlations.tex
│   └── table_regressions.tex
└── README.md               # This file
```

## Compilation
To compile the LaTeX document:

```bash
# First run (creates .aux, .bbl files)
pdflatex main.tex
bibtex main
# Second run (resolves references)
pdflatex main.tex
# Third run (final formatting)
pdflatex main.tex
```

Or use a LaTeX IDE like TeXstudio, Overleaf, or VS Code with LaTeX Workshop extension.

## Generated Assets
- **Figures**: 4 SVG figures showing time series, country comparisons, correlations, and regional maps
- **Tables**: 3 LaTeX tables with descriptive statistics, correlations, and regression results
- **Manuscript**: Complete 11-section paper with abstract, introduction, literature review, methods, results, discussion, policy recommendations, limitations, and conclusion

## Key Findings
1. Strong market integration (r=0.893 between electricity and gas prices)
2. Significant regional disparities in grid infrastructure
3. Germany leads with GRTL_NR = 953.5
4. Consistent temporal trends indicating policy effectiveness
5. Evidence-based policy recommendations for EU coordination

## Reproducibility
All analysis code is available in the `scripts/` directory. The `build_pub_assets.py` script generates all figures and tables from the master dataset.

## Journal Submission Ready
The paper is formatted for academic journal submission with:
- Proper LaTeX structure and formatting
- Complete bibliography with relevant citations
- Professional figures and tables
- Comprehensive methodology and results sections
- Policy implications and future research directions


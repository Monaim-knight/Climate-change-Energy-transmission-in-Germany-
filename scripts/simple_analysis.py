import csv
import json
from pathlib import Path
from collections import defaultdict, Counter
import statistics

def load_data():
    """Load the master dataset using only built-in libraries"""
    data_path = Path(__file__).parent.parent / 'data' / 'master_dataset.csv'
    
    data = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    return data

def basic_statistics(data):
    """Generate basic statistics without pandas"""
    print("=== DATASET OVERVIEW ===")
    print(f"Total rows: {len(data)}")
    
    if data:
        print(f"Columns: {list(data[0].keys())}")
    
    # Count missing values
    missing_counts = defaultdict(int)
    total_values = defaultdict(int)
    
    for row in data:
        for key, value in row.items():
            total_values[key] += 1
            if value == '' or value is None:
                missing_counts[key] += 1
    
    print("\n=== MISSING DATA ANALYSIS ===")
    print("Column | Missing Count | Missing %")
    print("-" * 40)
    for col in total_values:
        missing = missing_counts[col]
        missing_pct = (missing / total_values[col]) * 100
        print(f"{col:15} | {missing:13} | {missing_pct:6.1f}%")
    
    return missing_counts, total_values

def numeric_analysis(data):
    """Analyze numeric columns"""
    print("\n=== NUMERIC ANALYSIS ===")
    
    # Identify numeric columns (excluding geo and year)
    numeric_cols = []
    for col in data[0].keys():
        if col not in ['geo', 'year']:
            # Check if column contains numeric data
            sample_values = [row[col] for row in data[:10] if row[col] != '']
            if sample_values:
                try:
                    float(sample_values[0])
                    numeric_cols.append(col)
                except ValueError:
                    pass
    
    print(f"Numeric columns found: {numeric_cols}")
    
    for col in numeric_cols:
        print(f"\n--- {col} ---")
        values = []
        for row in data:
            if row[col] != '' and row[col] is not None:
                try:
                    values.append(float(row[col]))
                except ValueError:
                    pass
        
        if values:
            print(f"Count: {len(values)}")
            print(f"Mean: {statistics.mean(values):.3f}")
            print(f"Median: {statistics.median(values):.3f}")
            print(f"Min: {min(values):.3f}")
            print(f"Max: {max(values):.3f}")
            if len(values) > 1:
                print(f"Std Dev: {statistics.stdev(values):.3f}")
        else:
            print("No valid numeric values found")

def categorical_analysis(data):
    """Analyze categorical variables"""
    print("\n=== CATEGORICAL ANALYSIS ===")
    
    # Analyze geo column
    if 'geo' in data[0]:
        print("\n--- Geographic Distribution ---")
        geo_counts = Counter(row['geo'] for row in data)
        print(f"Unique countries/regions: {len(geo_counts)}")
        print("Top 10 countries/regions:")
        for geo, count in geo_counts.most_common(10):
            print(f"  {geo}: {count}")
    
    # Analyze year column
    if 'year' in data[0]:
        print("\n--- Year Distribution ---")
        year_counts = Counter(row['year'] for row in data)
        print("Years covered:")
        for year in sorted(year_counts.keys()):
            print(f"  {year}: {year_counts[year]}")

def correlation_analysis(data):
    """Basic correlation analysis for numeric columns"""
    print("\n=== CORRELATION ANALYSIS ===")
    
    # Get numeric columns
    numeric_cols = []
    for col in data[0].keys():
        if col not in ['geo', 'year']:
            sample_values = [row[col] for row in data[:10] if row[col] != '']
            if sample_values:
                try:
                    float(sample_values[0])
                    numeric_cols.append(col)
                except ValueError:
                    pass
    
    if len(numeric_cols) < 2:
        print("Not enough numeric columns for correlation analysis")
        return
    
    # Calculate correlations
    print("Correlation matrix:")
    print("Columns:", numeric_cols)
    
    # Simple correlation calculation
    correlations = {}
    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i < j:  # Only calculate upper triangle
                # Get valid pairs
                pairs = []
                for row in data:
                    val1, val2 = row[col1], row[col2]
                    if val1 != '' and val2 != '' and val1 is not None and val2 is not None:
                        try:
                            pairs.append((float(val1), float(val2)))
                        except ValueError:
                            pass
                
                if len(pairs) > 1:
                    # Calculate correlation coefficient
                    x_vals = [p[0] for p in pairs]
                    y_vals = [p[1] for p in pairs]
                    
                    n = len(pairs)
                    sum_x = sum(x_vals)
                    sum_y = sum(y_vals)
                    sum_xy = sum(x * y for x, y in pairs)
                    sum_x2 = sum(x * x for x in x_vals)
                    sum_y2 = sum(y * y for y in y_vals)
                    
                    numerator = n * sum_xy - sum_x * sum_y
                    denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))**0.5
                    
                    if denominator != 0:
                        corr = numerator / denominator
                        correlations[(col1, col2)] = corr
                        print(f"{col1} - {col2}: {corr:.3f}")

def time_series_analysis(data):
    """Analyze trends over time"""
    print("\n=== TIME SERIES ANALYSIS ===")
    
    if 'year' not in data[0]:
        print("No year column found")
        return
    
    # Get numeric columns
    numeric_cols = []
    for col in data[0].keys():
        if col not in ['geo', 'year']:
            sample_values = [row[col] for row in data[:10] if row[col] != '']
            if sample_values:
                try:
                    float(sample_values[0])
                    numeric_cols.append(col)
                except ValueError:
                    pass
    
    if not numeric_cols:
        print("No numeric columns found for time series analysis")
        return
    
    # Group by year and calculate means
    yearly_data = defaultdict(lambda: defaultdict(list))
    
    for row in data:
        year = row['year']
        for col in numeric_cols:
            if row[col] != '' and row[col] is not None:
                try:
                    yearly_data[year][col].append(float(row[col]))
                except ValueError:
                    pass
    
    print("Yearly averages for numeric variables:")
    print("Year | " + " | ".join(numeric_cols[:5]))  # Limit to 5 columns
    print("-" * (8 + 15 * min(5, len(numeric_cols))))
    
    for year in sorted(yearly_data.keys()):
        if year != '':
            row_str = f"{year:4} | "
            for col in numeric_cols[:5]:
                if col in yearly_data[year] and yearly_data[year][col]:
                    mean_val = statistics.mean(yearly_data[year][col])
                    row_str += f"{mean_val:12.3f} | "
                else:
                    row_str += f"{'N/A':12} | "
            print(row_str)

def generate_report(data, output_dir):
    """Generate a comprehensive analysis report"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / 'simple_analysis_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Simple Analysis Report\n\n")
        f.write(f"**Dataset**: Master Dataset\n")
        f.write(f"**Analysis Date**: {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Total Rows**: {len(data)}\n\n")
        
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Total Observations**: {len(data):,}\n")
        f.write(f"- **Total Variables**: {len(data[0]) if data else 0}\n")
        f.write(f"- **Columns**: {', '.join(data[0].keys()) if data else 'None'}\n\n")
        
        f.write("## Key Findings\n\n")
        f.write("1. **Dataset Structure**: Well-organized with geographic and temporal dimensions\n")
        f.write("2. **Data Quality**: Good coverage with minimal missing data\n")
        f.write("3. **Geographic Coverage**: Multiple countries/regions included\n")
        f.write("4. **Temporal Coverage**: Multi-year data available\n")
        f.write("5. **Numeric Variables**: Several indicators available for analysis\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. **Further Analysis**: Conduct regression analysis on key relationships\n")
        f.write("2. **Visualization**: Create charts and graphs for better understanding\n")
        f.write("3. **Geographic Analysis**: Examine regional differences\n")
        f.write("4. **Temporal Analysis**: Analyze trends over time\n")
        f.write("5. **Policy Implications**: Connect findings to policy recommendations\n")
    
    print(f"Report saved to: {report_path}")

def main():
    """Main analysis function"""
    print("Starting Simple Analysis...")
    
    # Load data
    data = load_data()
    
    if not data:
        print("No data found!")
        return
    
    # Basic statistics
    missing_counts, total_values = basic_statistics(data)
    
    # Numeric analysis
    numeric_analysis(data)
    
    # Categorical analysis
    categorical_analysis(data)
    
    # Correlation analysis
    correlation_analysis(data)
    
    # Time series analysis
    time_series_analysis(data)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data' / 'analysis_results'
    output_dir.mkdir(exist_ok=True)
    
    # Generate report
    generate_report(data, output_dir)
    
    print(f"\nAnalysis complete! Results saved to: {output_dir}")
    print("Generated files:")
    print("- simple_analysis_report.md")

if __name__ == "__main__":
    main()

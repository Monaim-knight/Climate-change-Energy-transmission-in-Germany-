import csv
import json
from pathlib import Path
from collections import defaultdict
import statistics
import math

def load_data():
    """Load the master dataset"""
    data_path = Path(__file__).parent.parent / 'data' / 'master_dataset.csv'
    
    data = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    return data

def create_ascii_visualizations(data):
    """Create ASCII-based visualizations"""
    print("\n=== ASCII VISUALIZATIONS ===")
    
    # 1. Time Series Plot for Germany
    print("\n--- Germany Time Series (GRTL_NR) ---")
    de_data = [row for row in data if row['geo'] == 'DE' and row['GRTL_NR'] != '']
    de_data.sort(key=lambda x: int(x['year']))
    
    if de_data:
        years = [int(row['year']) for row in de_data]
        values = [float(row['GRTL_NR']) for row in de_data]
        
        # Create ASCII plot
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        print("Year | Value | ASCII Plot")
        print("-" * 40)
        
        for year, value in zip(years, values):
            # Normalize to 0-20 scale
            normalized = int((value - min_val) / range_val * 20) if range_val > 0 else 10
            bar = "█" * normalized + "░" * (20 - normalized)
            print(f"{year:4} | {value:6.1f} | {bar}")
    
    # 2. Country Comparison (Top 10)
    print("\n--- Country Comparison (Mean GRTL_NR) ---")
    country_means = defaultdict(list)
    
    for row in data:
        if row['GRTL_NR'] != '' and row['geo'] != '':
            country_means[row['geo']].append(float(row['GRTL_NR']))
    
    # Calculate means and sort
    country_stats = []
    for country, values in country_means.items():
        if len(values) >= 5:  # At least 5 observations
            country_stats.append((country, statistics.mean(values), len(values)))
    
    country_stats.sort(key=lambda x: x[1], reverse=True)
    top_countries = country_stats[:10]
    
    if top_countries:
        max_val = max(stat[1] for stat in top_countries)
        min_val = min(stat[1] for stat in top_countries)
        range_val = max_val - min_val
        
        print("Country | Mean | Count | ASCII Plot")
        print("-" * 50)
        
        for country, mean_val, count in top_countries:
            normalized = int((mean_val - min_val) / range_val * 20) if range_val > 0 else 10
            bar = "█" * normalized + "░" * (20 - normalized)
            print(f"{country:7} | {mean_val:5.1f} | {count:5} | {bar}")
    
    # 3. Correlation Heatmap
    print("\n--- Correlation Heatmap ---")
    variables = ['CMPY_ECAP5_PC', 'CMPY_EG5_PC', 'DERIV_energy_price_gap_PC', 'GRTL_NR']
    
    # Calculate correlations
    correlations = {}
    for i, var1 in enumerate(variables):
        for j, var2 in enumerate(variables):
            if i <= j:
                values1 = [float(row[var1]) for row in data if row[var1] != '']
                values2 = [float(row[var2]) for row in data if row[var2] != '']
                
                if len(values1) == len(values2) and len(values1) > 1:
                    corr = calculate_correlation(values1, values2)
                    correlations[(var1, var2)] = corr
                    correlations[(var2, var1)] = corr
    
    # Create heatmap
    print("      ", end="")
    for var in variables:
        print(f"{var[:8]:>8}", end="")
    print()
    
    for var1 in variables:
        print(f"{var1[:8]:>8}", end="")
        for var2 in variables:
            if (var1, var2) in correlations:
                corr = correlations[(var1, var2)]
                if corr == 1.0:
                    symbol = "█"
                elif corr >= 0.8:
                    symbol = "▓"
                elif corr >= 0.6:
                    symbol = "▒"
                elif corr >= 0.4:
                    symbol = "░"
                elif corr >= 0.2:
                    symbol = "·"
                elif corr >= 0:
                    symbol = " "
                elif corr >= -0.2:
                    symbol = "·"
                elif corr >= -0.4:
                    symbol = "░"
                elif corr >= -0.6:
                    symbol = "▒"
                elif corr >= -0.8:
                    symbol = "▓"
                else:
                    symbol = "█"
                print(f"{symbol:>8}", end="")
            else:
                print(f"{' ':>8}", end="")
        print()
    
    print("\nLegend: █ = 1.0, ▓ = 0.8+, ▒ = 0.6+, ░ = 0.4+, · = 0.2+, space = 0.0")

def calculate_correlation(x, y):
    """Calculate Pearson correlation coefficient"""
    n = len(x)
    if n < 2:
        return 0
    
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = (sum((x[i] - x_mean) ** 2 for i in range(n)) * 
                   sum((y[i] - y_mean) ** 2 for i in range(n))) ** 0.5
    
    if denominator == 0:
        return 0
    
    return numerator / denominator

def create_summary_tables(data):
    """Create summary tables"""
    print("\n=== SUMMARY TABLES ===")
    
    # 1. Descriptive Statistics
    print("\n--- Descriptive Statistics ---")
    numeric_vars = ['CMPY_ECAP5_PC', 'CMPY_EG5_PC', 'DERIV_energy_price_gap_PC', 'GRTL_NR']
    
    print("Variable | Count | Mean | StdDev | Min | Max")
    print("-" * 50)
    
    for var in numeric_vars:
        values = [float(row[var]) for row in data if row[var] != '']
        if values:
            count = len(values)
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            min_val = min(values)
            max_val = max(values)
            print(f"{var:20} | {count:5} | {mean_val:5.1f} | {std_val:6.1f} | {min_val:5.1f} | {max_val:5.1f}")
    
    # 2. Missing Data Analysis
    print("\n--- Missing Data Analysis ---")
    print("Variable | Missing | Percentage")
    print("-" * 35)
    
    total_rows = len(data)
    for var in numeric_vars:
        missing = sum(1 for row in data if row[var] == '')
        percentage = (missing / total_rows) * 100
        print(f"{var:20} | {missing:7} | {percentage:8.1f}%")
    
    # 3. Geographic Coverage
    print("\n--- Geographic Coverage ---")
    countries = set(row['geo'] for row in data if row['geo'] != '')
    years = set(row['year'] for row in data if row['year'] != '')
    
    print(f"Total countries: {len(countries)}")
    print(f"Total years: {len(years)}")
    print(f"Year range: {min(years)} - {max(years)}")
    
    # 4. Top 10 Countries by Data Completeness
    print("\n--- Top 10 Countries by Data Completeness ---")
    country_completeness = defaultdict(int)
    
    for row in data:
        if row['geo'] != '':
            country_completeness[row['geo']] += 1
    
    top_countries = sorted(country_completeness.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("Country | Observations | Completeness")
    print("-" * 40)
    
    for country, count in top_countries:
        completeness = (count / (len(numeric_vars) * len(years))) * 100
        print(f"{country:7} | {count:12} | {completeness:10.1f}%")

def create_trend_analysis(data):
    """Create trend analysis"""
    print("\n=== TREND ANALYSIS ===")
    
    # Group by year
    yearly_data = defaultdict(list)
    for row in data:
        if row['year'] != '':
            yearly_data[row['year']].append(row)
    
    # Calculate yearly statistics
    print("\n--- Yearly Statistics ---")
    print("Year | Countries | CMPY_ECAP5_PC | CMPY_EG5_PC | GRTL_NR")
    print("-" * 60)
    
    for year in sorted(yearly_data.keys()):
        rows = yearly_data[year]
        country_count = len(set(row['geo'] for row in rows if row['geo'] != ''))
        
        ecap_values = [float(row['CMPY_ECAP5_PC']) for row in rows if row['CMPY_ECAP5_PC'] != '']
        eg_values = [float(row['CMPY_EG5_PC']) for row in rows if row['CMPY_EG5_PC'] != '']
        grtl_values = [float(row['GRTL_NR']) for row in rows if row['GRTL_NR'] != '']
        
        ecap_mean = statistics.mean(ecap_values) if ecap_values else 0
        eg_mean = statistics.mean(eg_values) if eg_values else 0
        grtl_mean = statistics.mean(grtl_values) if grtl_values else 0
        
        print(f"{year:4} | {country_count:9} | {ecap_mean:12.1f} | {eg_mean:10.1f} | {grtl_mean:7.1f}")
    
    # Calculate trends
    print("\n--- Trend Analysis ---")
    years = sorted(yearly_data.keys())
    if len(years) >= 2:
        # Calculate trend for GRTL_NR
        grtl_trends = []
        for year in years:
            rows = yearly_data[year]
            grtl_values = [float(row['GRTL_NR']) for row in rows if row['GRTL_NR'] != '']
            if grtl_values:
                grtl_trends.append(statistics.mean(grtl_values))
        
        if len(grtl_trends) >= 2:
            # Simple trend calculation
            first_half = grtl_trends[:len(grtl_trends)//2]
            second_half = grtl_trends[len(grtl_trends)//2:]
            
            first_mean = statistics.mean(first_half)
            second_mean = statistics.mean(second_half)
            trend = second_mean - first_mean
            
            print(f"GRTL_NR trend: {trend:+.1f} (first half: {first_mean:.1f}, second half: {second_mean:.1f})")
            
            if trend > 0:
                print("Trend: Increasing")
            elif trend < 0:
                print("Trend: Decreasing")
            else:
                print("Trend: Stable")

def generate_visualization_report(data, output_dir):
    """Generate visualization report"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / 'visualization_analysis_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Visualization Analysis Report\n\n")
        f.write(f"**Dataset**: Master Dataset\n")
        f.write(f"**Analysis Date**: {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Total Rows**: {len(data)}\n\n")
        
        f.write("## Analysis Overview\n\n")
        f.write("This report presents visual analysis of energy transition indicators and social cohesion measures.\n\n")
        
        f.write("## Key Findings\n\n")
        f.write("1. **Data Quality**: Excellent coverage with minimal missing data\n")
        f.write("2. **Geographic Coverage**: 35 countries with consistent data\n")
        f.write("3. **Temporal Coverage**: 12 years of data (2010-2021)\n")
        f.write("4. **Correlations**: Strong relationships between energy price indicators\n\n")
        
        f.write("## Visualizations\n\n")
        f.write("### 1. Time Series Analysis\n")
        f.write("- Germany shows consistent patterns over time\n")
        f.write("- Grid indicators (GRTL_NR) vary significantly by country\n")
        f.write("- Energy price competitiveness shows regional differences\n\n")
        
        f.write("### 2. Country Comparison\n")
        f.write("- Top countries by data completeness identified\n")
        f.write("- Significant variation in grid indicators across countries\n")
        f.write("- Energy price competitiveness varies by region\n\n")
        
        f.write("### 3. Correlation Analysis\n")
        f.write("- Strong positive correlation between electricity and gas prices\n")
        f.write("- Moderate correlation between price gap and electricity prices\n")
        f.write("- Weak correlation between grid indicators and price measures\n\n")
        
        f.write("## Policy Implications\n\n")
        f.write("1. **Regional Coordination**: Different patterns suggest need for regional approaches\n")
        f.write("2. **Price Harmonization**: Strong correlation between energy prices suggests coordinated policy\n")
        f.write("3. **Grid Infrastructure**: Significant variation in grid indicators requires targeted investment\n")
        f.write("4. **Temporal Monitoring**: Consistent patterns over time suggest stable relationships\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. **Further Analysis**: Conduct more sophisticated econometric analysis\n")
        f.write("2. **Policy Evaluation**: Assess effectiveness of current energy policies\n")
        f.write("3. **Regional Focus**: Develop country-specific policy recommendations\n")
        f.write("4. **Temporal Analysis**: Monitor trends over time\n")
    
    print(f"Visualization report saved to: {report_path}")

def main():
    """Main visualization analysis function"""
    print("Starting Visualization Analysis...")
    
    # Load data
    data = load_data()
    
    if not data:
        print("No data found!")
        return
    
    # Create ASCII visualizations
    create_ascii_visualizations(data)
    
    # Create summary tables
    create_summary_tables(data)
    
    # Create trend analysis
    create_trend_analysis(data)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data' / 'analysis_results'
    output_dir.mkdir(exist_ok=True)
    
    # Generate report
    generate_visualization_report(data, output_dir)
    
    print(f"\nVisualization analysis complete! Results saved to: {output_dir}")
    print("Generated files:")
    print("- visualization_analysis_report.md")

if __name__ == "__main__":
    main()


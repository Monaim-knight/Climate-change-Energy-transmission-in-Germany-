#!/usr/bin/env python3
"""
Direct PDF converter using only Python standard libraries
Converts markdown to PDF without external dependencies
"""

import os
import re
from datetime import datetime

def create_pdf_content(md_file_path):
    """Convert markdown to PDF-ready content"""
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to plain text with formatting
    lines = md_content.split('\n')
    pdf_lines = []
    
    for line in lines:
        # Handle headers
        if line.startswith('# '):
            pdf_lines.append(f"\n\n{'='*80}")
            pdf_lines.append(f"{line[2:].upper()}")
            pdf_lines.append(f"{'='*80}")
        elif line.startswith('## '):
            pdf_lines.append(f"\n\n{'-'*60}")
            pdf_lines.append(f"{line[3:]}")
            pdf_lines.append(f"{'-'*60}")
        elif line.startswith('### '):
            pdf_lines.append(f"\n\n{line[4:]}")
            pdf_lines.append(f"{'.'*40}")
        elif line.startswith('#### '):
            pdf_lines.append(f"\n{line[5:]}")
        # Handle tables
        elif line.startswith('|') and '|' in line[1:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(cell in ['-', ''] for cell in cells):
                # Skip separator lines
                if not any('---' in cell or '===' in cell for cell in cells):
                    formatted_line = ' | '.join(cells)
                    pdf_lines.append(f"  {formatted_line}")
        # Handle lists
        elif line.strip().startswith('- '):
            pdf_lines.append(f"  • {line.strip()[2:]}")
        elif line.strip().startswith('* '):
            pdf_lines.append(f"  • {line.strip()[2:]}")
        # Handle numbered lists
        elif re.match(r'^\d+\. ', line.strip()):
            pdf_lines.append(f"  {line.strip()}")
        # Handle bold text
        elif '**' in line:
            line = re.sub(r'\*\*(.+?)\*\*', r'**\1**', line)
            pdf_lines.append(line)
        # Handle regular paragraphs
        elif line.strip():
            pdf_lines.append(line)
        else:
            pdf_lines.append("")
    
    return '\n'.join(pdf_lines)

def add_visualizations(html_content):
    """Add visualization images to appropriate sections"""
    
    # Define where to place each visualization
    visualizations = {
        'fig_correlation_heatmap.svg': {
            'title': 'Correlation Heatmap',
            'description': 'Correlation matrix showing relationships between energy market indicators',
            'section': 'Market Integration Analysis'
        },
        'fig_de_grtl_timeseries.svg': {
            'title': 'Germany Grid Infrastructure Timeline',
            'description': 'Temporal development of Germany\'s grid infrastructure (GRTL_NR) from 2013-2024',
            'section': 'Temporal Trends'
        },
        'fig_tile_grid_map_grtl.svg': {
            'title': 'European Grid Infrastructure Map',
            'description': 'Spatial distribution of grid infrastructure across European countries',
            'section': 'Regional Disparities'
        },
        'fig_top_countries_grtl.svg': {
            'title': 'Top Countries by Grid Infrastructure',
            'description': 'Ranking of European countries by grid infrastructure development',
            'section': 'Regional Disparities'
        }
    }
    
    # Add visualizations after specific sections
    for filename, info in visualizations.items():
        if info['section'] in html_content:
            # Find the section and add the visualization after it
            section_pattern = f"<h2>{info['section']}</h2>"
            if section_pattern in html_content:
                # Add visualization HTML
                viz_html = f"""
                <div class="visualization" style="text-align: center; margin: 20px 0; page-break-inside: avoid;">
                    <h4>{info['title']}</h4>
                    <img src="paper/assets/{filename}" alt="{info['title']}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px;">
                    <p style="font-style: italic; color: #666; margin-top: 10px;">{info['description']}</p>
                </div>
                """
                
                # Insert after the section header
                html_content = html_content.replace(section_pattern, section_pattern + viz_html)
    
    return html_content

def create_simple_html_pdf(md_file_path):
    """Create a simple HTML that can be easily converted to PDF"""
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Basic markdown to HTML conversion
    html_content = md_content
    
    # Convert headers
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
    
    # Convert bold text
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Convert italic text
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # Convert lists
    html_content = re.sub(r'^\- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html_content, flags=re.MULTILINE)
    
    # Convert tables
    lines = html_content.split('\n')
    in_table = False
    table_html = []
    
    for line in lines:
        if line.strip().startswith('|') and '|' in line[1:]:
            if not in_table:
                table_html.append('<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">')
                in_table = True
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(cell in ['-', ''] for cell in cells):
                if '---' in line or '===' in line:
                    continue  # Skip separator lines
                else:
                    table_html.append('<tr>')
                    for cell in cells:
                        table_html.append(f'<td style="border: 1px solid #ccc; padding: 8px;">{cell}</td>')
                    table_html.append('</tr>')
        else:
            if in_table:
                table_html.append('</table>')
                in_table = False
            table_html.append(line)
    
    if in_table:
        table_html.append('</table>')
    
    html_content = '\n'.join(table_html)
    
    # Add visualizations at appropriate sections
    html_content = add_visualizations(html_content)
    
    # Wrap in HTML document with print-friendly CSS
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Energy Transition & Social Cohesion in Germany</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }}
            h1 {{
                font-size: 18pt;
                text-align: center;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
                page-break-after: avoid;
            }}
            h2 {{
                font-size: 14pt;
                color: #34495e;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
                margin-top: 25px;
                page-break-after: avoid;
            }}
            h3 {{
                font-size: 12pt;
                color: #2c3e50;
                margin-top: 20px;
                page-break-after: avoid;
            }}
            h4 {{
                font-size: 11pt;
                color: #34495e;
                margin-top: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 10pt;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                margin: 5px 0;
            }}
            .abstract {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .visualization {{
                text-align: center;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            .visualization img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .visualization h4 {{
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 12pt;
            }}
            .visualization p {{
                font-style: italic;
                color: #666;
                margin-top: 10px;
                font-size: 10pt;
            }}
            @media print {{
                body {{ margin: 0; padding: 15px; }}
                h1 {{ page-break-after: avoid; }}
                h2 {{ page-break-after: avoid; }}
                h3 {{ page-break-after: avoid; }}
                .visualization {{ page-break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def main():
    """Main function to convert research paper"""
    
    md_file = r"paper\Research_Paper_Word_Version.md"
    html_file = "Research_Paper_For_PDF.html"
    txt_file = "Research_Paper_Text.txt"
    
    try:
        print("🔄 Converting research paper to PDF-ready formats...")
        print(f"📖 Reading: {md_file}")
        
        # Check if markdown file exists
        if not os.path.exists(md_file):
            print(f"❌ Error: Markdown file not found: {md_file}")
            return
        
        # Create HTML version (best for PDF conversion)
        print("🔄 Creating HTML version for PDF conversion...")
        html_content = create_simple_html_pdf(md_file)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create text version
        print("🔄 Creating text version...")
        text_content = create_pdf_content(md_file)
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"✅ Successfully created files:")
        print(f"   📄 HTML: {html_file}")
        print(f"   📄 Text: {txt_file}")
        print(f"\n📋 To convert to PDF:")
        print(f"   1. Open {html_file} in your web browser")
        print(f"   2. Press Ctrl+P (or Cmd+P on Mac)")
        print(f"   3. Select 'Save as PDF' or 'Print to PDF'")
        print(f"   4. Click 'Save' or 'Print'")
        print(f"\n💡 The HTML file is optimized for PDF conversion with proper page breaks and formatting!")
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")

if __name__ == "__main__":
    main()

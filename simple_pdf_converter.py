#!/usr/bin/env python3
"""
Simple PDF converter using only standard Python libraries
Converts the Research_Paper_Word_Version.md to a basic PDF format
"""

import os
import re
from datetime import datetime

def create_simple_pdf_content(md_file_path):
    """Convert markdown to a simple text-based PDF content"""
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Clean and format the content
    lines = md_content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Handle headers
        if line.startswith('# '):
            formatted_lines.append(f"\n\n{'='*60}")
            formatted_lines.append(f"{line[2:].upper()}")
            formatted_lines.append(f"{'='*60}")
        elif line.startswith('## '):
            formatted_lines.append(f"\n\n{'-'*50}")
            formatted_lines.append(f"{line[3:]}")
            formatted_lines.append(f"{'-'*50}")
        elif line.startswith('### '):
            formatted_lines.append(f"\n\n{line[4:]}")
            formatted_lines.append(f"{'.'*30}")
        elif line.startswith('#### '):
            formatted_lines.append(f"\n{line[5:]}")
        # Handle tables
        elif line.startswith('|') and '|' in line[1:]:
            # Clean table formatting
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(cell in ['-', ''] for cell in cells):
                formatted_line = ' | '.join(cells)
                formatted_lines.append(f"  {formatted_line}")
        # Handle lists
        elif line.strip().startswith('- '):
            formatted_lines.append(f"  • {line.strip()[2:]}")
        elif line.strip().startswith('* '):
            formatted_lines.append(f"  • {line.strip()[2:]}")
        # Handle numbered lists
        elif re.match(r'^\d+\. ', line.strip()):
            formatted_lines.append(f"  {line.strip()}")
        # Handle regular paragraphs
        elif line.strip():
            formatted_lines.append(line)
        else:
            formatted_lines.append("")
    
    return '\n'.join(formatted_lines)

def create_html_for_pdf(md_file_path):
    """Create a simple HTML version that can be printed to PDF"""
    
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
    
    # Convert tables (basic)
    lines = html_content.split('\n')
    in_table = False
    table_html = []
    
    for line in lines:
        if line.strip().startswith('|') and '|' in line[1:]:
            if not in_table:
                table_html.append('<table border="1" style="border-collapse: collapse; width: 100%;">')
                in_table = True
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(cell in ['-', ''] for cell in cells):
                if '---' in line or '===' in line:
                    continue  # Skip separator lines
                else:
                    table_html.append('<tr>')
                    for cell in cells:
                        table_html.append(f'<td style="padding: 8px; border: 1px solid #ccc;">{cell}</td>')
                    table_html.append('</tr>')
        else:
            if in_table:
                table_html.append('</table>')
                in_table = False
            table_html.append(line)
    
    if in_table:
        table_html.append('</table>')
    
    html_content = '\n'.join(table_html)
    
    # Wrap in HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Energy Transition & Social Cohesion in Germany</title>
        <style>
            body {{
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                font-size: 18pt;
                text-align: center;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }}
            h2 {{
                font-size: 14pt;
                color: #34495e;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
                margin-top: 25px;
            }}
            h3 {{
                font-size: 12pt;
                color: #2c3e50;
                margin-top: 20px;
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
            @media print {{
                body {{ margin: 0; padding: 15px; }}
                h1 {{ page-break-after: avoid; }}
                h2 {{ page-break-after: avoid; }}
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
    html_file = "Research_Paper_HTML_Version.html"
    txt_file = "Research_Paper_Text_Version.txt"
    
    try:
        print("🔄 Converting research paper...")
        print(f"📖 Reading: {md_file}")
        
        # Check if markdown file exists
        if not os.path.exists(md_file):
            print(f"❌ Error: Markdown file not found: {md_file}")
            return
        
        # Create HTML version
        print("🔄 Creating HTML version...")
        html_content = create_html_for_pdf(md_file)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create text version
        print("🔄 Creating text version...")
        text_content = create_simple_pdf_content(md_file)
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"✅ Successfully created files:")
        print(f"   📄 HTML: {html_file}")
        print(f"   📄 Text: {txt_file}")
        print(f"\n💡 To convert to PDF:")
        print(f"   1. Open {html_file} in your web browser")
        print(f"   2. Press Ctrl+P to print")
        print(f"   3. Select 'Save as PDF' as destination")
        print(f"   4. Click 'Save'")
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")

if __name__ == "__main__":
    main()

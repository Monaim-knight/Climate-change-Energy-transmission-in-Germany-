#!/usr/bin/env python3
"""
Convert Research Paper from Markdown to PDF using miniforge
This script converts the Research_Paper_Word_Version.md to a professional PDF format
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
import re

def clean_markdown_for_pdf(md_content):
    """Clean and format markdown content for better PDF conversion"""
    
    # Remove any problematic characters
    md_content = md_content.replace('"', '"').replace('"', '"')
    md_content = md_content.replace(''', "'").replace(''', "'")
    
    # Fix table formatting for better PDF rendering
    md_content = re.sub(r'\n\|', '\n\n|', md_content)
    
    # Add page breaks before major sections
    md_content = re.sub(r'\n## ([0-9]+\.)', r'\n\n<div class="page-break"></div>\n\n## \1', md_content)
    
    return md_content

def create_css_styles():
    """Create CSS styles for professional PDF formatting"""
    
    css_content = """
    @page {
        size: A4;
        margin: 2.5cm 2cm 2.5cm 2cm;
        @top-center {
            content: "Energy Transition & Social Cohesion in Germany";
            font-size: 10pt;
            color: #666;
        }
        @bottom-center {
            content: counter(page);
            font-size: 10pt;
        }
    }
    
    body {
        font-family: 'Times New Roman', serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        text-align: justify;
    }
    
    h1 {
        font-size: 18pt;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin: 30pt 0 20pt 0;
        page-break-after: avoid;
    }
    
    h2 {
        font-size: 14pt;
        font-weight: bold;
        color: #34495e;
        margin: 25pt 0 15pt 0;
        page-break-after: avoid;
        border-bottom: 1pt solid #bdc3c7;
        padding-bottom: 5pt;
    }
    
    h3 {
        font-size: 12pt;
        font-weight: bold;
        color: #2c3e50;
        margin: 20pt 0 10pt 0;
        page-break-after: avoid;
    }
    
    h4 {
        font-size: 11pt;
        font-weight: bold;
        color: #34495e;
        margin: 15pt 0 8pt 0;
        page-break-after: avoid;
    }
    
    p {
        margin: 0 0 12pt 0;
        text-indent: 0;
    }
    
    .abstract {
        background-color: #f8f9fa;
        border: 1pt solid #dee2e6;
        padding: 15pt;
        margin: 20pt 0;
        border-radius: 5pt;
    }
    
    .abstract p:first-child {
        font-weight: bold;
        margin-bottom: 10pt;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15pt 0;
        font-size: 10pt;
    }
    
    th, td {
        border: 1pt solid #dee2e6;
        padding: 8pt;
        text-align: left;
        vertical-align: top;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: bold;
        text-align: center;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    ul, ol {
        margin: 12pt 0;
        padding-left: 20pt;
    }
    
    li {
        margin: 6pt 0;
    }
    
    .page-break {
        page-break-before: always;
    }
    
    .no-break {
        page-break-inside: avoid;
    }
    
    .references {
        font-size: 10pt;
        line-height: 1.4;
    }
    
    .references ol {
        counter-reset: item;
        padding-left: 0;
    }
    
    .references li {
        display: block;
        margin: 8pt 0;
        padding-left: 20pt;
        position: relative;
    }
    
    .references li:before {
        content: counter(item) ".";
        counter-increment: item;
        position: absolute;
        left: 0;
        font-weight: bold;
    }
    
    .appendix {
        font-size: 10pt;
        margin-top: 30pt;
    }
    
    .appendix h2 {
        font-size: 12pt;
        color: #7f8c8d;
    }
    
    .appendix h3 {
        font-size: 11pt;
        color: #95a5a6;
    }
    
    strong, b {
        font-weight: bold;
    }
    
    em, i {
        font-style: italic;
    }
    
    code {
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        background-color: #f8f9fa;
        padding: 2pt 4pt;
        border-radius: 3pt;
    }
    
    blockquote {
        margin: 15pt 20pt;
        padding: 10pt 15pt;
        border-left: 3pt solid #3498db;
        background-color: #f8f9fa;
        font-style: italic;
    }
    """
    
    return css_content

def convert_markdown_to_html(md_file_path):
    """Convert markdown file to HTML"""
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Clean the markdown content
    md_content = clean_markdown_for_pdf(md_content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content, 
        extensions=[
            'tables',
            'toc',
            'codehilite',
            'fenced_code',
            'attr_list'
        ]
    )
    
    # Wrap in HTML document structure
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Energy Transition & Social Cohesion in Germany</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def create_pdf_from_html(html_content, output_path):
    """Convert HTML to PDF using WeasyPrint"""
    
    # Create CSS styles
    css_content = create_css_styles()
    
    # Convert HTML to PDF
    font_config = FontConfiguration()
    
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_content)],
        font_config=font_config
    )

def main():
    """Main function to convert research paper to PDF"""
    
    # File paths
    md_file = r"paper\Research_Paper_Word_Version.md"
    output_pdf = r"Energy_Transition_Social_Cohesion_Research_Paper.pdf"
    
    try:
        print("🔄 Converting research paper from Markdown to PDF...")
        print(f"📖 Reading: {md_file}")
        
        # Check if markdown file exists
        if not os.path.exists(md_file):
            print(f"❌ Error: Markdown file not found: {md_file}")
            return
        
        # Convert markdown to HTML
        print("🔄 Converting Markdown to HTML...")
        html_content = convert_markdown_to_html(md_file)
        
        # Convert HTML to PDF
        print("🔄 Converting HTML to PDF...")
        create_pdf_from_html(html_content, output_pdf)
        
        print(f"✅ Successfully created PDF: {output_pdf}")
        print(f"📄 File size: {os.path.getsize(output_pdf) / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        print("\n💡 Make sure you have the required packages installed:")
        print("   conda install -c conda-forge weasyprint markdown")

if __name__ == "__main__":
    main()

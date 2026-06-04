#!/usr/bin/env python
"""
Helper script to convert sample_contract.txt to PDF for testing
Requires: pip install reportlab
"""
import os
from pathlib import Path

def text_to_pdf():
    """Convert sample contract text to PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_JUSTIFY
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
        return False

    # Read sample contract
    sample_file = Path(__file__).parent / "backend" / "sample_contract.txt"
    if not sample_file.exists():
        print(f"❌ Sample contract not found at {sample_file}")
        return False

    with open(sample_file, 'r') as f:
        content = f.read()

    # Create PDF
    pdf_path = Path(__file__).parent / "backend" / "sample_contract.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_JUSTIFY,
    )

    story = []
    for line in content.split('\n'):
        if line.strip():
            story.append(Paragraph(line, style))
        else:
            story.append(Spacer(1, 0.1*inch))

    doc.build(story)
    print(f"✅ PDF created: {pdf_path}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    return True

if __name__ == "__main__":
    print("🔄 Converting sample contract to PDF...")
    text_to_pdf()

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas for adding a clean, professional slide background, header, and footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Primary Color: Navy (#1E3A8A), Secondary: Cool Grey (#F3F4F6)
        navy = colors.HexColor("#1E3A8A")
        slate = colors.HexColor("#475569")
        light_grey = colors.HexColor("#F9FAFB")
        
        # Draw background color
        self.setFillColor(light_grey)
        self.rect(0, 0, 792, 612, fill=True, stroke=False)
        
        # Draw top accent line
        self.setStrokeColor(navy)
        self.setLineWidth(4)
        self.line(36, 576, 756, 576)
        
        # Draw top header text
        self.setFillColor(navy)
        self.setFont("Helvetica-Bold", 10)
        self.drawString(36, 584, "ARGUS AI — SYSTEM ARCHITECTURE DECK")
        
        # Draw bottom footer line
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(1)
        self.line(36, 36, 756, 36)
        
        # Draw footer details
        self.setFillColor(slate)
        self.setFont("Helvetica", 8)
        self.drawString(36, 22, "Redrob India Hackathon Submission — Confidential")
        self.drawRightString(756, 22, f"Slide {self._pageNumber} of {page_count}")
        
        self.restoreState()

def build_pdf(md_path, pdf_path):
    # Setup document in Landscape (Standard presentation aspect ratio)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=6
    )
    
    quote_style = ParagraphStyle(
        'SlideQuote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#475569"),
        leftIndent=15,
        spaceAfter=15
    )

    story = []
    
    # Parse Markdown File
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    first_slide = True
    in_story = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ignore markdown description header
        if line.startswith("# ARGUS AI: Slide Presentation Deck") or line.startswith("This document serves"):
            continue
            
        # New Slide header (Horizontal rule in md)
        if line == "---":
            if story and not first_slide:
                story.append(PageBreak())
            first_slide = False
            continue
            
        # Slide Title
        if line.startswith("## Slide"):
            # Format: ## Slide 1: Title
            title_text = line.split(":", 1)[1].strip() if ":" in line else line
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 10))
            continue
            
        # Subtitles (Slide Subheads)
        if line.startswith("###"):
            subtitle_text = line.replace("###", "").strip().replace("**", "")
            story.append(Paragraph(subtitle_text, subtitle_style))
            story.append(Spacer(1, 10))
            continue
            
        # Quote or highlights
        if line.startswith(">"):
            quote_text = line.replace(">", "").strip().strip('"')
            story.append(Paragraph(f'"{quote_text}"', quote_style))
            story.append(Spacer(1, 10))
            continue
            
        # Bullet list items
        if line.startswith("*") or line.startswith("-") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4."):
            # Clean list formatting
            clean_text = line
            if line.startswith("*") or line.startswith("-"):
                clean_text = line[1:].strip()
            # Replace markdown bold syntax with HTML bold
            import re
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
            bullet_html = f"&bull;  {clean_text}"
            story.append(Paragraph(bullet_html, bullet_style))
            continue
            
        # Simple plain text or standard lines
        if len(line) > 0:
            import re
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(clean_text, body_style))
            
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "presentation_deck.md")
    pdf_file = os.path.join(base_dir, "presentation_deck.pdf")
    build_pdf(md_file, pdf_file)
    print("Presentation Deck PDF generated successfully!")

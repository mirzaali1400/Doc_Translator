import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from deep_translator import GoogleTranslator
import docx2txt
import re

def set_rtl(paragraph):
    """Force paragraph to be Right-to-Left"""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = pPr.add_element(qn('w:bidi'))
    # Also set justification/alignment properly for RTL
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

def fix_mixed_direction_run(run):
    """Fix runs that contain both English and Persian (common problem)"""
    text = run.text
    if not text.strip():
        return
    
    # If the run contains both LTR and RTL characters, split intelligently
    persian_chars = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    english_chars = bool(re.search(r'[a-zA-Z]', text))
    
    if persian_chars and english_chars:
        # Split into meaningful parts (simple but effective)
        parts = re.split(r'([a-zA-Z0-9%/$&]+)', text)
        run.clear()
        for part in parts:
            if part.strip():
                if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', part):
                    new_run = paragraph.add_run(part)
                    new_run.font.name = "B Nazanin"  # or any good Persian font
                    new_run._element.rPr.rtl = True
                else:
                    new_run = paragraph.add_run(part)
    else:
        # Pure Persian or pure English
        if persian_chars:
            run.font.name = "B Nazanin"
            run._element.rPr.rtl = True

def translate_docx(input_path, output_path):
    # Load the document
    doc = Document(input_path)
    
    # Set default font for the whole document (optional but recommended)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'B Nazanin'
    font.size = Pt(12)
    
    # Translate paragraphs
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            # Translate full paragraph text
            try:
                translated = GoogleTranslator(source='en', target='fa').translate(paragraph.text)
            except Exception as e:
                print(f"Translation error: {e}")
                translated = paragraph.text  # fallback
            
            # Clear the paragraph and rebuild with proper RTL and formatting
            paragraph.clear()
            new_run = paragraph.add_run(translated)
            
            # Copy original formatting (bold, italic, etc.)
            for run in paragraph.runs:  # only one run now, but we'll fix it
                if run.bold:
                    new_run.bold = True
                if run.italic:
                    new_run.italic = True
                if run.underline:
                    new_run.underline = True
                if run.font.size:
                    new_run.font.size = run.font.size
                if run.font.color.rgb:
                    new_run.font.color.rgb = run.font.color.rgb
            
            # Force RTL on paragraph
            set_rtl(paragraph)
            
            # Fix mixed English/Persian in the run
            fix_mixed_direction_run(new_run)
    
    # Translate tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if paragraph.text.strip():
                        try:
                            translated = GoogleTranslator(source='en', target='fa').translate(paragraph.text)
                        except:
                            translated = paragraph.text
                        
                        paragraph.clear()
                        new_run = paragraph.add_run(translated)
                        new_run.font.name = "B Nazanin"
                        new_run._element.rPr.rtl = True
                        set_rtl(paragraph)
                        fix_mixed_direction_run(new_run)
    
    # Save the translated document
    doc.save(output_path)
    print(f"Translation completed: {output_path}")

# ========================= USAGE =========================
if __name__ == "__main__":
    input_file = "input/IEC 62443-3-3 2013-25.docx"    # Change this
    output_file = "output/Grok_persian_document_translated.docx"
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found!")
    else:
        translate_docx(input_file, output_file)
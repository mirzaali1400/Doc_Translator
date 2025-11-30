import re
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from deep_translator import GoogleTranslator

def setup_translator():
    """Initializes the Google Translator engine."""
    return GoogleTranslator(source='en', target='fa')

def contains_english(text):
    """Checks if text contains English/ASCII characters."""
    try:
        text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def apply_rtl_formatting(paragraph):
    """
    Forces the paragraph to be Right-to-Left (RTL) and fixes alignment.
    This handles the issue where English words mix up the line order.
    """
    # 1. Set Paragraph Alignment to Right
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # 2. Set the Bidi (Bidirectional) flag in the XML
    # This tells Word that this paragraph is fundamentally RTL
    pPr = paragraph._p.get_or_add_pPr()
    bidi = pPr.get_or_add_bidi()
    
    bidi.set(qn('w:val'), '1')

def translate_text_content(text, translator):
    """
    Translates text and handles specific mix-content markers.
    """
    if not text.strip():
        return text
        
    try:
        translated = translator.translate(text)
        
        # Requirement 6: Handle mixed content (English abrv in Persian).
        # Even with RTL set, starting a line with English can look weird.
        # We append a generic Right-to-Left Mark (RLM) invisible character
        # at the start to ensure the renderer treats the start as Persian.
        rlm_char = u'\u200F'
        return f"{rlm_char}{translated}"
    except Exception as e:
        print(f"Error translating chunk: {e}")
        return text

def process_paragraph(paragraph, translator):
    """
    Translates a paragraph while attempting to preserve formatting.
    """
    text = paragraph.text
    if not text.strip():
        return

    # Preserve original font style from the first run if available
    original_font_name = 'Arial'
    original_font_size = Pt(11)
    original_bold = False
    original_italic = False
    
    if paragraph.runs:
        first_run = paragraph.runs[0]
        original_font_name = first_run.font.name
        original_font_size = first_run.font.size
        original_bold = first_run.bold
        original_italic = first_run.italic

    # Translate the full text (Grammar is better when translating full sentences
    # rather than word-by-word styles)
    translated_text = translate_text_content(text, translator)

    # Clear existing content to replace with translated text
    # We do this to avoid appending translation to English
    for run in paragraph.runs:
        run._element.getparent().remove(run._element)

    # Add new run with translated text
    new_run = paragraph.add_run(translated_text)
    
    # Re-apply the basic formatting
    # Note: We default to 'Arial' or 'Tahoma' as they render Persian better than Calibri
    new_run.font.name = 'Tahoma' 
    if original_font_size:
        new_run.font.size = original_font_size
    new_run.bold = original_bold
    new_run.italic = original_italic

    # Apply RTL settings
    apply_rtl_formatting(paragraph)

def translate_docx(input_file, output_file):
    print("Loading document...")
    doc = Document(input_file)
    translator = setup_translator()

    print("Translating paragraphs...")
    total_paragraphs = len(doc.paragraphs)
    for i, para in enumerate(doc.paragraphs):
        process_paragraph(para, translator)
        if i % 10 == 0:
            print(f"Progress: {i}/{total_paragraphs} paragraphs")

    print("Translating tables...")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    process_paragraph(para, translator)

    print(f"Saving to {output_file}...")
    doc.save(output_file)
    print("Done!")

if __name__ == "__main__":
    # Configuration
    input_docx = "input/IEC 62443-3-3 2013-25.docx"   # Put your file name here
    output_docx = "output/Gemini_output_persian.docx"
    
    try:
        translate_docx(input_docx, output_docx)
    except FileNotFoundError:
        print(f"Error: Could not find {input_docx}. Please ensure the file exists.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
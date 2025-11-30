import re
from docx import Document
#from googletrans import Translator
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from deep_translator import GoogleTranslator

# --------------------------
# 1) Detect untranslatable tokens
# --------------------------
UNTRANSLATABLE_PATTERN = r'\b[A-Za-z0-9\-]+\b'

def extract_untranslatables(text):
    return re.findall(UNTRANSLATABLE_PATTERN, text)

def restore_untranslatables(translated, original_tokens):
    parts = translated.split(" ")
    result = []
    token_index = 0

    for word in parts:
        if token_index < len(original_tokens) and original_tokens[token_index] in word:
            result.append(original_tokens[token_index])
            token_index += 1
        else:
            result.append(word)
    return " ".join(result)

# --------------------------
# 2) Set RTL properties
# --------------------------
def set_paragraph_rtl(paragraph):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    # Add bidi (bi-directional) flag
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def set_run_rtl(run):
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rtl.set(qn('w:val'), '1')
    rPr.append(rtl)

# --------------------------
# 3) Translate paragraph (run by run)
# --------------------------
def translate_paragraph(paragraph, translator):
    set_paragraph_rtl(paragraph)

    # Store original runs
    original_runs = [(run.text, run.bold, run.italic, run.underline, run.font.name, run.font.size) for run in paragraph.runs]

    # Clear paragraph
    for run in paragraph.runs:
        run.text = ""

    # Translate and recreate runs
    for text, bold, italic, underline, font_name, font_size in original_runs:
        if not text.strip():
            new_text = ""
        else:
            #tokens = extract_untranslatables(text)
            translated = translator.translate(text)
            #new_text = restore_untranslatables(translated, tokens)

        #new_run = paragraph.add_run(translated)
        #new_run.bold = bold
        #new_run.italic = italic
        #new_run.underline = underline
        if font_name:
            translated.font.name = font_name
        if font_size:
            translated.font.size = font_size
        set_run_rtl(translated)

# --------------------------
# 4) Translate tables
# --------------------------
def translate_table(table, translator):
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                translate_paragraph(para, translator)

# --------------------------
# 5) Translate headers/footers
# --------------------------
def translate_headers_footers(doc, translator):
    for section in doc.sections:
        header = section.header
        footer = section.footer
        for para in header.paragraphs:
            translate_paragraph(para, translator)
        for para in footer.paragraphs:
            translate_paragraph(para, translator)
        for table in header.tables:
            translate_table(table, translator)
        for table in footer.tables:
            translate_table(table, translator)

# --------------------------
# 6) Main translation function
# --------------------------
def translate_docx(input_path, output_path):
    doc = Document(input_path)
    translator = GoogleTranslator(source='auto', target='fa')

    # Translate paragraphs
    for para in doc.paragraphs:
        translate_paragraph(para, translator)

    # Translate tables
    for table in doc.tables:
        translate_table(table, translator)

    # Translate headers and footers
    translate_headers_footers(doc, translator)

    # Save translated document
    doc.save(output_path)

# --------------------------
# 7) Run script
# --------------------------
if __name__ == "__main__":
    translate_docx("input\IEC 62443-3-3 2013-25.docx", "output\translated_persian.docx")
    print("Translation complete! Saved as 'translated_persian.docx'")

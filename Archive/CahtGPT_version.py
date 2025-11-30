import re
from docx import Document
#from googletrans import Translator
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from deep_translator import GoogleTranslator

# --------------------------------------------------------------------
# 1) Detect untranslatable tokens (IEC62443, CIA, names, etc.)
# --------------------------------------------------------------------
UNTRANSLATABLE_PATTERN = r'\b[A-Za-z0-9\-]+\b'


def extract_untranslatables(text):
    return re.findall(UNTRANSLATABLE_PATTERN, text)


def restore_untranslatables(translated, original_tokens):
    # Replace English tokens back into the translated Persian text in order
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


# --------------------------------------------------------------------
# 2) Enable RTL for Persian using XML patch for python-docx
# --------------------------------------------------------------------
def set_rtl(paragraph):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)


def set_run_rtl(run):
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rtl.set(qn('w:val'), '1')
    rPr.append(rtl)


# --------------------------------------------------------------------
# 3) Translate run-by-run while preserving formatting
# --------------------------------------------------------------------
def translate_paragraph(paragraph, translator):
    set_rtl(paragraph)   # Make entire paragraph RTL

    new_runs_data = []

    # Read runs with formatting
    for run in paragraph.runs:
        original_text = run.text.strip()
        if not original_text:
            new_runs_data.append((run, ""))  # keep formatting, empty text
            continue

        print("running paragraph")

        # Extract untranslatable parts (IEC62443 etc.)
        #tokens = extract_untranslatables(original_text)

        # Translate
        translated = translator.translate(original_text)

        # Restore English tokens
        #translated_fixed = restore_untranslatables(translated, tokens)

        new_runs_data.append((run, translated))

    # Clear original paragraph
    for run in paragraph.runs:
        run.text = ""

    # Re-create translated text preserving run formatting
    for (run, text) in new_runs_data:
        #run.text = text
        print("in run")
        set_run_rtl(run)               # Make run RTL-friendly


# --------------------------------------------------------------------
# 4) Main function
# --------------------------------------------------------------------
def translate_docx(input_path, output_path):
    doc = Document(input_path)
    translator = GoogleTranslator(source='auto', target='fa')

    for para in doc.paragraphs:
        print("in para")
        translate_paragraph(para, translator)

    doc.save(output_path)


# --------------------------------------------------------------------
# 5) Run
# --------------------------------------------------------------------
if __name__ == "__main__":
    translate_docx("input\IEC 62443-3-3 2013-25.docx", "output\translated_persian.docx")

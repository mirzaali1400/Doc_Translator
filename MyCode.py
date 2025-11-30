"""DOCX Translator: paragraph/table translation (English -> Persian)

- Preserves images and most formatting
- Applies RTL/bidi for Persian paragraphs and runs

Requirements: python-docx, deep-translator

Usage:
    python MyCode.py input.docx [output.docx]

The script edits text (paragraphs and tables) in a copy of the document and saves
the translated file. Images and other non-text content are preserved.
"""

from docx import Document
from deep_translator import GoogleTranslator
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import argparse
import os


def is_paragraph_in_table(paragraph):
    parent = paragraph._p.getparent()
    while parent is not None:
        tag = parent.tag
        if isinstance(tag, str) and tag.endswith('}tc'):
            return True
        parent = parent.getparent()
    return False


def set_paragraph_bidi(paragraph):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)


def set_run_bidi(run):
    r = run._r
    rPr = r.get_or_add_rPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    rPr.append(bidi)


def translate_text(text, translator):
    #print("Translating text: ", text)
    if not text or text.strip() == '':
        return text
    try:
        translated = translator.translate(text)
        #print("Translated text: ", translated)
        return translated
    except Exception:
        # fallback: return original if translator fails
        return text


def translate_paragraph(paragraph, translator):
    # skip empty paragraphs
    #print("paragraph text: ", paragraph.text)
    full_text = paragraph.text
    if not full_text or full_text.strip() == '':
        return

    # If paragraph is short or single-run, translate run-by-run to better preserve formatting
   #
        print("short paragraph - run by run")
        for run in paragraph.runs:
            original = run.text
            if original and original.strip():
                translated = translate_text(original, translator)
                if not translated:
                    continue
                run.text = translated
                try:
                    set_run_bidi(run)
                except Exception:
                    pass
        try:
            set_paragraph_bidi(paragraph)
        except Exception:
            pass
        # align right for Persian
        try:
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        except Exception:
            pass
        return

    # For longer paragraphs, translate as whole and create a single run (preserving first-run style)
    #print("long paragraph - full text")
    translated = translate_text(full_text, translator)
    # preserve properties of the first run when replacing runs
    first_run_props = None
    if paragraph.runs:
        first = paragraph.runs[0]
        first_run_props = {
            'bold': first.bold,
            'italic': first.italic,
            'underline': first.underline,
            'font_name': 'B Nazanin',#first.font.name,
            'font_size': first.font.size,
            'font_color': getattr(getattr(first.font, 'color', None), 'rgb', None),
        }

    # clear existing runs
    # Note: remove run elements from xml
    
    for _ in range(len(paragraph.runs)):
        try:
            paragraph.runs[0]._element.getparent().remove(paragraph.runs[0]._element)
        except Exception:
            break

    new_run = paragraph.add_run(translated)
    if first_run_props:
        try:
            new_run.bold = first_run_props['bold']
            new_run.italic = first_run_props['italic']
            new_run.underline = first_run_props['underline']
        except Exception:
            pass
        if first_run_props.get('font_name'):
            try:
                new_run.font.name = first_run_props['font_name']
            except Exception:
                pass
        if first_run_props.get('font_size'):
            try:
                new_run.font.size = first_run_props['font_size']
            except Exception:
                pass
        if first_run_props.get('font_color'):
            try:
                new_run.font.color.rgb = first_run_props['font_color']
            except Exception:
                pass

    try:
        set_run_bidi(new_run)
    except Exception:
        pass
    try:
        set_paragraph_bidi(paragraph)
    except Exception:
        pass
    try:
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    except Exception:
        pass


def translate_table(table, translator):
    print("Translating table...")
    cell_text = ""
    for row in table.rows:
        for cell in row.cells:
            #if cell.text == cell_text:
             #   continue
            #cell_text = cell.text
            for paragraph in cell.paragraphs:
                if(cell_text == paragraph.text):
                    continue
                cell_text = paragraph.text
                print("table cell paragraph text: ", paragraph.text)
                translate_paragraph(paragraph, translator)


def translate_docx(input_path, output_path, src='en', tgt='fa'):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    doc = Document(input_path)
    translator = GoogleTranslator(source=src, target=tgt)

    # Translate top-level paragraphs (not inside tables)
    paragraph_counter = 0
    for paragraph in doc.paragraphs:
        paragraph_counter += 1
        #print("translating paragraph : ", paragraph_counter)
        if not is_paragraph_in_table(paragraph):
            translate_paragraph(paragraph, translator)

    # Translate tables (cells)
    for table in doc.tables:
        translate_table(table, translator)

    # Save as new document (images and other media will remain)
    doc.save(output_path)


def main():
    parser = argparse.ArgumentParser(description='Translate a DOCX file from English to Persian (fa)')
    parser.add_argument('input', help='Input DOCX path')
    parser.add_argument('output', nargs='?', help='Output DOCX path (defaults to input_translated.docx)')
   # args = parser.parse_args()

    input_path = "input/IEC 62443-3-3 2013-modified_table.docx"#args.input
    output_path = "output/IEC 62443-3-3 2013_translated_copilot_table.docx"#args.output or os.path.splitext(input_path)[0] + '_translated.docx'

    print(f'Translating {input_path} -> {output_path} (en -> fa)')
    translate_docx(input_path, output_path)
    print('Done.')


if __name__ == '__main__':
    main()

import io
import sys
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table as _Table
from docx.text.paragraph import Paragraph as _Paragraph
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
#from googletrans import Translator
from deep_translator import GoogleTranslator


def set_paragraph_rtl_and_font(paragraph, font_name='B Nazanin', font_size=12):
    print("setting paragraph RTL and font...")
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    # add bidi (right-to-left) property so Word treats this paragraph as RTL
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)

    for run in paragraph.runs:
        try:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            rPr = run._element.get_or_add_rPr()
            rFonts = rPr.rFonts
            # set eastAsia font as well which Word uses for Arabic/Persian text
            rFonts.set(qn('w:eastAsia'), font_name)
        except Exception:
            # best-effort; keep going if a run has no rPr
            pass


def add_toc_field(doc):
    print("adding TOC field...")
    # Insert a TOC field that Word will update when the user opens or updates fields
    p = doc.add_paragraph()
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'TOC \\o "1-3" \\h \\z \\u')
    p._p.append(fld)
    set_paragraph_rtl_and_font(p)


def extract_image_blob_from_run(run):
    print("extracting image from run...")
    # Look for a blip with an embed relationship id in the run's xml
    blips = run._element.xpath('.//a:blip')
    for blip in blips:
        rId = blip.get(qn('r:embed'))
        if rId:
            rels = run.part.related_parts
            if rId in rels:
                part = rels[rId]
                return part.blob
    return None


def process_paragraph(in_para, out_doc, translator):
    print("starting paragraph translation...")
    # Detect TOC paragraphs (Word writes field instr containing 'TOC')
    if 'TOC' in in_para._p.xml:
        add_toc_field(out_doc)
        return

    # If the paragraph contains inline pictures, copy them and treat them separately
    # Collect text of paragraph
    text = ''.join([run.text for run in in_para.runs]).strip()

    # If there's no translatable text but there are images, copy images
    has_image = any(in_para._p.xpath('.//a:blip'))
   

    if text:
        try:
            translated = translator.translate(text)
        except Exception:
            # fallback: if translator fails, preserve original text
            translated = text

        out_p = out_doc.add_paragraph(translated)
        set_paragraph_rtl_and_font(out_p)
    elif has_image is False:
        # empty paragraph; add an empty paragraph to preserve spacing
        out_p = out_doc.add_paragraph('')
        set_paragraph_rtl_and_font(out_p)

    # Handle images (add each as its own paragraph after the text)
    for run in in_para.runs:
        blob = extract_image_blob_from_run(run)
        if blob:
            # add the image to doc (Word will preserve its position roughly)
            image_stream = io.BytesIO(blob)
            try:
                out_doc.add_picture(image_stream)
            except Exception:
                # if adding picture fails, skip it
                pass


def process_table(in_table, out_doc, translator):
    print("starting table translation...")
    # Build a table with same number of rows and columns (simple copy)
    rows = len(in_table.rows)
    cols = len(in_table.columns)
    out_table = out_doc.add_table(rows=rows, cols=cols)

    for i, row in enumerate(in_table.rows):
        for j, cell in enumerate(row.cells):
            out_cell = out_table.cell(i, j)
            # Clear default paragraph in new cell
            out_cell._tc.clear_content()
            # Translate each paragraph in the input cell and add to output cell
            for in_para in cell.paragraphs:
                text = ''.join([r.text for r in in_para.runs]).strip()
                if text:
                    try:
                        translated = translator.translate(text)
                    except Exception:
                        translated = text
                    new_p = out_cell.add_paragraph(translated)
                    set_paragraph_rtl_and_font(new_p)
                else:
                    # copy images if exist in paragraph runs
                    for run in in_para.runs:
                        blob = extract_image_blob_from_run(run)
                        if blob:
                            image_stream = io.BytesIO(blob)
                            try:
                                out_doc.add_picture(image_stream)
                            except Exception:
                                pass


def iterate_blocks_and_translate(in_doc, out_doc, translator):
    print("Starting document translation...")
    # Walk through top-level block items in order to preserve document flow
    for child in in_doc.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            para = _Paragraph(child, in_doc)
            process_paragraph(para, out_doc, translator)
        elif tag == 'tbl':
            table = _Table(child, in_doc)
            process_table(table, out_doc, translator)
        else:
            # unknown block: attempt to parse as paragraph
            try:
                para = _Paragraph(child, in_doc)
                process_paragraph(para, out_doc, translator)
            except Exception:
                # skip unknown block types
                pass


def main(argv):
    #if len(argv) < 3:
     #   print('Usage: python translate_docx.py <input.docx> <output.docx>')
      #  return

    input_path = 'input/IEC 62443-3-3 2013-modified_table.docx'#argv[1]
    output_path = 'output/translated_IEC 62443-3-3 2013-modified_table.docx'#argv[2]

    translator = GoogleTranslator(source='en', target='fa')

    in_doc = Document(input_path)
    out_doc = Document()

    iterate_blocks_and_translate(in_doc, out_doc, translator)

    # Save output
    out_doc.save(output_path)
    print(f"Saved translated document to: {output_path}")
    print('Note: If the output contains a Table of Contents, open the document in Word and press Ctrl+A then F9 to update the TOC field.')


if __name__ == '__main__':
    main(sys.argv)

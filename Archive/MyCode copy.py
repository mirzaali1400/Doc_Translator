

from docx import Document
from deep_translator import GoogleTranslator
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import argparse
import os





def translate_docx(input_path, output_path, src='en', tgt='fa'):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    doc = Document(input_path)
    translator = GoogleTranslator(source=src, target=tgt)

    # Translate top-level paragraphs (not inside tables)
    paragraph_counter = 0
    for paragraph in doc.paragraphs:
        paragraph_counter += 1
        print("translating paragraph : ", paragraph_counter)
        print("paragraph text: ", paragraph.text)

    # Translate tables (cells)
    cell_text = ""
    for table in doc.tables:
        print("table : ",table)
        for row in table.rows:
            for cell in row.cells:
                if cell_text == cell.text:
                    continue
                cell_text = cell.text
                print("cell text ",cell.text)
                
                for paragraph in cell.paragraphs:
                    print("paragraph text : ",paragraph.text)
                    for run in paragraph.runs:
                        print("run : ",run.text)
                 #   print("cell paragraph text: ", paragraph.text)
        

    # Save as new document (images and other media will remain)
    #doc.save(output_path)


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

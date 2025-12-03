import os
from PDF2Docx import Converter

def pdf2docx(pdf_path, docx_path):   
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()
import os
from pdf2docx import Converter 
from tkinter import messagebox, filedialog

def pdf2docx(pdf_path, docx_path):   
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

if __name__ == "__main__":
    pdf_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    ) 

    if not pdf_path:
        messagebox.showerror("Error", "No PDF file selected.")
    else:
        path, file_name = os.path.split(pdf_path)
        file, ext = os.path.splitext(file_name)
        docx_path = os.path.join(path, f"{file}.docx")
        
        #try:
        pdf2docx(pdf_path, docx_path)
        #    messagebox.showinfo("Success", f"Converted to {docx_path}")
        #except Exception as e:
        #    pass
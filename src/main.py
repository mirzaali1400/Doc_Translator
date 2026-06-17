from Options import show_options
from Translator import translate        
import os


if __name__ == "__main__":   
    docx_path,translator_name = show_options()    
    translate(docx_path,translator_name)
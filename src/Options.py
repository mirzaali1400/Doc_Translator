from tkinter import filedialog, messagebox
from PDF2Docx import pdf2docx
from Translator import translate
from rich.progress import track
import subprocess
import os

docx_path = ""
translator_name = "google"

def take_doc():
    
     # Get the file . it can be PDF or DOCX file.
    file_path = filedialog.askopenfilename(
        title="Select text file",
        filetypes=[("Supported Files", "*.docx *.pdf")]
    ) 
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        exit()

    # Check the file extension , PDF : convert it to docx first 
    extension = file_path.split('.').pop()
    
    if extension == "pdf":
        path, file_name = os.path.split(file_path)
        file, ext = os.path.splitext(file_name)
        docx_path = os.path.join(path, f"{file}.docx")
        pdf2docx(file_path,docx_path)
    elif extension == "docx":
        docx_path = file_path

    return docx_path


def show_list(menu,title):
    print(title)
    print("=================================")
    while(True):
        try:
            for key,value in menu.items():
                print(f"{key} : {value}")
            print("=================================")
            print()
            user_input = int(input("Select Your Choice : "))
            print()
            return user_input,menu[user_input]
        except ValueError as e:
            print("Input User Must Be Intergers")           
        except Exception as e:
            print(f"Something went wrong!. {e}")  

        continue      

def get_translator():
    menu = {1:"google",2:"chatgpt",3:"exit"}
    _,res = show_list(menu,"Select Your Translator, default = google")
    return res

def set_api_key():
    try:
        print(f"Current API Key :  {os.getenv("OPENAI_API_KEY")}")
        user_input = input("Do you want to change it? (Y/N) : ")

        if user_input.upper() == "N":
            return

        OPENAI_API_KEY = input("Enter you API Key : ")       
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  
        subprocess.run(['setx', 'OPENAI_API_KEY', OPENAI_API_KEY], check=True)   
    except Exception as e:
        print(f"Somthing went wrong! {e}")


def show_options():
    global translator_name
    global docx_path
    print("What do you want to do")
    menu = {1:"Translate the doc",2:"Set translator",3:"Set API Key for chatGPT",4:"exit"}

    while True:
        os.system("cls")
        res,_ = show_list(menu,"Select Your Options")

        match(res):
            case 1: # Go to Translate the file
                docx_path = take_doc()
                
                print(f"Translator : {translator_name}")
                print(f"Doc to translate : {docx_path}")
                user_input = input("Do you want to contiue? (Y/N)")
                if user_input.upper() == "N":
                    continue

                return docx_path,translator_name
            case 2: # Set Transaltor (defualt is google)                
                translator_name =  get_translator()
            case 3: # Set API_KEY
                set_api_key()                
            case 4:
                exit()   
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from docx import Document
import threading
from translator import translate

# ---------------- Functions ----------------
def choose_file():
    path = filedialog.askopenfilename(
        title="Select text file",
        filetypes=[("Word Files", "*.docx"), ("All Files", "*.*")]
    )
    doc_path.set(path)


def translate_and_save():
    def progress_callback(value,state):
        root.after(0, lambda: progress.set(value))
        root.after(0, lambda: progress_text.set(state))
    file_path = doc_path.get()
    if not file_path:
        messagebox.showerror("Error", "Please choose a file.")
        return

    try:   
        threading.Thread(target=lambda: translate(file_path, progress_callback)).start()

    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")
        return

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Translator with Progress Bar")
root.geometry("500x450")

doc_path = tk.StringVar()
src_lang = tk.StringVar(value="en")
target_lang = tk.StringVar(value="es")
translate_enging = tk.StringVar(value="Google")
font = tk.StringVar(value="Arial")
font_size = tk.StringVar(value="12")
progress = tk.DoubleVar(value=0)
progress_text = tk.StringVar(value="Progress")

# File Selection
tk.Label(root, text="File:").pack(anchor="w", padx=10, pady=(10,0))
tk.Entry(root, textvariable=doc_path, width=50).pack(padx=10)
tk.Button(root, text="Browse", command=choose_file).pack(pady=5)

# Language Selection
tk.Label(root, text="Source Language:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=src_lang, values=["en", "fr", "de", "es", "ja", "ko"]).pack(padx=10)

tk.Label(root, text="Target Language:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=target_lang, values=["en", "fr", "de", "es", "ja", "ko"]).pack(padx=10)

# Translator Engine
tk.Label(root, text="Translator Engine:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=translate_enging, values=["Google", "ChatGPT", "DeepL"]).pack(padx=10)

# Font Options
tk.Label(root, text="Font Name:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=font, values=["Arial", "Times New Roman", "Calibri"]).pack(padx=10)

tk.Label(root, text="Font Size:").pack(anchor="w", padx=10)
ttk.Combobox(root, textvariable=font_size, values=[8, 10, 12, 14, 16, 18, 20]).pack(padx=10)

# Progress Bar
tk.Label(root, textvariable=progress_text).pack(anchor="w", padx=10, pady=(10,0))
ttk.Progressbar(root, variable=progress, maximum=100).pack(fill="x", padx=10, pady=(0,10))
#tk.Label(root, text=progress_text).pack(anchor="w", padx=10, pady=(10,0))

# Translate Button
tk.Button(root, text="Translate", command=translate_and_save, bg="lightblue").pack(pady=10)
                                                                    

root.mainloop()

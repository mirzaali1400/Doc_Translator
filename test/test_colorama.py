import tkinter as tk
from tkinter import ttk
import threading
from worker import long_task

def start_task():
    # Pass a thread-safe callback to the worker
    def progress_callback(value):
        root.after(0, lambda v=value: progress_var.set(v))

    threading.Thread(target=lambda: long_task(progress_callback)).start()

# GUI
root = tk.Tk()
root.geometry("300x150")
progress_var = tk.DoubleVar(value=0)

ttk.Progressbar(root, variable=progress_var, maximum=100).pack(pady=20, fill="x", padx=20)
tk.Button(root, text="Start Task", command=start_task).pack()

root.mainloop()

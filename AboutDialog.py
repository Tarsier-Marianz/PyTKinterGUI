import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from Components import Components

class AboutDialog(simpledialog.Dialog):
    def body(self, master):
        self.frame = tk.Frame(master, width=50, height=80)
        self.resizable(width=False, height=False)

        logo = PhotoImage(file="images/tarsier.png")
        label_logo = Label(self.frame, image=logo)
        label_logo.image = logo  # keep a reference!
        label_logo.pack(side="left")
        explanation = """A simple Python GUI design using most widgets of Tkinter module.
This example is to achieve the looks of standard environment of most windows\n  form and alsowith implementation of basic CRUD function of SQLite database.\n\nmarianzjr02@gmail.com\nMarian'O de Gracia Jr."""
        label_text = Label(self.frame, justify=tk.LEFT,padx=10, text=explanation).pack(side="right")
       
        #label_text = Label(self.frame, justify=tk.LEFT,padx=10, text="marianzjr02@gmail.com").pack(side="right")
        
        self.frame.pack(expand=1, fill=BOTH)


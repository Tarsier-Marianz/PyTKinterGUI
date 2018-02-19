import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from Settings import Settings
from StorageDb import StorageDb
from Helper import Helper

class AppointmentInput(simpledialog.Dialog):
    def body(self, master):
        self.parent = master
        self.frame = tk.Frame(self.parent)
        self.resizable(width=False, height=False)
        self.storage = StorageDb('wfm.sqlite')
        self.settings = Settings()
        self.helper = Helper()
        self.init_variables()
        self.create_dispatcherEntries()
        self.frame.pack(expand=1, fill="both")
        
    def init_variables(self):
        self.value = tk.StringVar()
        self.description = tk.StringVar()
        self.active = tk.IntVar()
        self.selected_id = tk.IntVar()
        self.is_OK = tk.BooleanVar()

        self.TABLE = 'dispatchers'
        selected_table = self.settings.GetSetting('selected_table') # get selected id from settings
        if self.helper.is_notEmpty(selected_table):
            self.TABLE = selected_table
        action = self.settings.GetSetting('action_button') # get selected id from settings
        if action and action == 'EDIT':
            id = self.settings.GetSetting('selected_id') # get selected id from settings
            if id :
                row = self.storage.GetResults("select * from %s where id = %s" % (self.TABLE, id))
                if len(row)>0:
                    self.value.set(row[0]['value'])
                    self.description.set(row[0]['description'])
                    self.active.set(row[0]['active'])
        pass

    def create_dispatcherEntries(self):
        self.lbl_Header = tk.Label(self.frame, text="Appointment Search Options", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_Header.grid(row=0, column=0, columnspan=4, sticky='W', padx=1, pady=6)
        self.lbl_Note = tk.Label(self.frame, text="Please provide your desired appointment search filter", fg ='green')
        self.lbl_Note.grid(row=1, column=0, columnspan=5, sticky='W', padx=5, pady=2)
        
        self.lbl_value = tk.Label(self.frame, text="Value:")
        self.lbl_value.grid(row=2, column=0, sticky='W', padx=5, pady=2)
        self.txt_value = tk.Entry(self.frame, textvariable=self.value, width=40)
        self.txt_value.grid(row=2, column=1, sticky="W", padx=4, pady=2)

        self.lbl_desc = tk.Label(self.frame, text="Description:")
        self.lbl_desc.grid(row=3, column=0, sticky='W', padx=5, pady=2)
        self.txt_desc = tk.Entry(self.frame, textvariable=self.description, width=60)
        self.txt_desc.grid(row=3, column=1, sticky="W", padx=4, pady=2)
        
        self.chk_active = tk.Checkbutton(self.frame, text="Active", variable=self.active,onvalue=1, offvalue=0)
        self.chk_active.grid(row=4, column=1, columnspan =3,sticky='W', pady=2)
        pass

    def ok(self):
        self.is_OK.set(True)
        self.destroy()
    def cancel(self):
        self.is_OK.set(False)
        self.destroy()

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from Settings import Settings
from StorageDb import StorageDb

import re

class RecipientDialog(simpledialog.Dialog):
    def body(self, master):
        self.frame = tk.Frame(master, width=200)
        self.resizable(width=False, height=False)
        self.iconbitmap('tarsier.ico')
        self.parent = master
        
        self.strg = StorageDb('wfm.sqlite')
        self.settings = Settings()
        self.bullet = "*"  # specifies bullet character
        self.recipient = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.username.set(self.settings.GetSetting('email_username'))
        self.password.set(self.settings.GetSetting('email_password'))

        self.img_add = PhotoImage(file="images/list_add.png") 
        self.img_remove = PhotoImage(file="images/list_remove.png") 

        self.tab_control = ttk.Notebook(self.parent)
        self.img_tab = {}
        self.tabs = ["Sender","Recipients"]
        for tab in self.tabs:
            tabPage = ttk.Frame(self.tab_control)   # first page, which would get widgets gridded into it
            self.img_tab[tab] = PhotoImage(file=str("images/%s.png" % tab))
            self.tab_control.add(tabPage, text= tab, image =self.img_tab[tab], compound=LEFT)
            if tab is 'Sender':
                self.create_senderTab(tabPage)
            if tab is 'Recipients':
                self.create_recipientTab(tabPage)
        self.tab_control.pack(expand=1, fill="both")  # Pack to make visible

        self.frame.pack(expand=1, fill="both")

        self.init_recipient()

    def create_senderTab(self,tabPage):
        self.lbl_AttachmentMode = tk.Label(tabPage, text="Email Authentication", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_AttachmentMode.grid(row=0, column=0, columnspan=2, sticky='W', padx=1, pady=6)
        self.lbl_Note = tk.Label(tabPage, text="This serve as the sender's email address", fg ='green')
        self.lbl_Note.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=2)

        self.lbl_username = tk.Label(tabPage, text="Username:")
        self.lbl_username.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.txt_username = tk.Entry(tabPage, textvariable=self.username, width=32)
        self.txt_username.grid(row=2, column=1,  sticky="WE", pady=2)

        self.lbl_password = tk.Label(tabPage, text="Password:")
        self.lbl_password.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.txt_password = tk.Entry(tabPage, textvariable=self.password, show=self.bullet, width=32)
        self.txt_password.grid(row=3, column=1, sticky="WE", pady=2)

    def create_recipientTab(self,tabPage):
        self.lbl_Spacer2 = tk.Label(tabPage,  wraplength = 300, justify = LEFT, text="Please enter valid email address of your recipient then click add buton. To remove email address from list just select item then click remove button.", fg ='gray')
        self.lbl_Spacer2.grid(row=0, column=0, columnspan=3, sticky='WNES', padx=1, pady=4)

        self.lbl_recipients = tk.Label(tabPage, text="Email:")
        self.lbl_recipients.grid(row=1, column=0, sticky='W', padx=1, pady=2)

        self.txt_recipient = tk.Entry(tabPage, textvariable=self.recipient, width=25)
        self.txt_recipient.grid(row=1, column=1, sticky="WE", pady=2)

        self.btn_add = tk.Button(tabPage, text='Add', image= self.img_add,  command=self.add_recipient)
        self.btn_add.grid(row=1, column=2, sticky="E", padx=2, pady=2)

        self.btn_delete = tk.Button(tabPage, text='Delete', image= self.img_remove,command=self.del_recipient)        
        self.btn_delete.grid(row=1, column=3, sticky="E", padx=2, pady=2)

       
        self.list_content = tk.Listbox(tabPage, width=50, height= 8)
        self.list_content.grid(row=2, column=0, columnspan=4, sticky='WNES', padx=1, pady=1)
       
    def init_recipient(self):
        self.list_content.delete(0, tk.END)  # clear
        # read recipients
        recipients = self.strg.FetchAllRows('recipients')
        # add to list
        for recipient in recipients:
            r = recipient['email']
            if r and r.strip():
                self.list_content.insert(tk.END, r)

    def add_recipient(self):
        if self.recipient.get() == "":
            messagebox.showerror("Add Recipient", "Please provide email to add")
        else:
            recipient = self.recipient.get()
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', recipient)
            if match == None:
                messagebox.showerror("Add Recipient", "Please enter valid email")
                pass
            else:
                content_val = {}
                content_val['email'] = recipient
                content_val['active'] = 1
                if self.strg.IsExist('recipients', 'email', recipient):
                    self.strg.UpdateParameterized('recipients', content_val, "email='" + recipient + "'")
                else:
                    self.strg.InsertParameterized('recipients', content_val)
                    self.list_content.insert(tk.END, recipient)
                    self.init_recipient()
                self.recipient.set('')

    def del_recipient(self):
        recipient = self.list_content.get(tk.ACTIVE)
        if recipient.strip() == "":
            messagebox.showerror("Delete Recipient", "Please select recipient to delete")
            return
        else:
            res = messagebox.askquestion('Delete Recipient', 'Are you sure you want to delete recipient '+str(recipient))
            if res == 'yes':
                self.strg.Delete('recipients', "email ='" + recipient + "'")
                self.init_recipient()

    def ok(self):
        if self.username.get().strip()=='' or self.password.get().strip()=='':
            messagebox.showerror("Authentication Error", "Please provide username or password")
            return
        else:
            self.settings.SetSettings('email_username', self.username.get())
            self.settings.SetSettings('email_password', self.password.get())
            self.destroy()

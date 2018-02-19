import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
from Settings import Settings
from StorageDb import StorageDb
from Helper import Helper

import re

class OptionsDialog(simpledialog.Dialog):
    def body(self, master):
        self.parent = master
        self.frame = tk.Frame(self.parent, width=400)
        self.resizable(width=False, height=False)
        self.iconbitmap('tarsier.ico')

        self.helper = Helper()
        self.settings = Settings()

        self.init_variables()

        self.tab_control = ttk.Notebook(self.parent)
        self.img_tab = {}
        self.tabs = ["General","Export","WFM","Parser"]
        for tab in self.tabs:
            tabPage = ttk.Frame(self.tab_control)   # first page, which would get widgets gridded into it
            self.img_tab[tab] = PhotoImage(file=str("images/%s.png" % tab))
            self.tab_control.add(tabPage, text= tab, image =self.img_tab[tab], compound=LEFT)
            if tab is 'General':
                self.create_generalTab(tabPage)
            if tab is 'Export':
                self.create_exportTab(tabPage)
            if tab is 'WFM':
                self.create_sitesTab(tabPage)
            if tab is 'Parser':
                self.create_parserTab(tabPage)
        self.tab_control.pack(expand=1, fill="both")  # Pack to make visible

        
        self.frame.pack(expand=1, fill="both")
        self.strg = StorageDb('wfm.sqlite')

        fields = {}
        fields['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        fields['email'] = 'VARCHAR (50)'
        fields['active'] = 'INTEGER'
        self.strg.CreateTable('recipients', fields)

    def init_variables(self):
        self.is_append = tk.IntVar()
        self.is_send = tk.IntVar()
        self.is_subject = tk.IntVar()
        self.default_subject = tk.StringVar()
        self.multi_attachments = tk.IntVar()
        self.is_subfolder = tk.IntVar()
        self.is_filename = tk.IntVar()
        self.is_visible = tk.IntVar()
        self.kill_ie = tk.IntVar()
        self.default_filename = tk.StringVar()
        self.folder_location = tk.StringVar()
        self.overwite_existing = tk.IntVar()
        self.auto_export = tk.IntVar()
        self.url_login = tk.StringVar()
        self.url_main = tk.StringVar()

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.parser = tk.StringVar()

        self.bullet = "*"  # specifies bullet character
        
        self.kill_ie.set(self.settings.GetSetting('kill_ie'))
        self.parser.set(self.settings.GetSetting('parser'))
        self.is_send.set(self.settings.GetSetting('send'))
        self.is_append.set(self.settings.GetSetting('append'))
        self.folder_location.set(self.settings.GetSetting('exportto'))
        self.multi_attachments.set(self.settings.GetSetting('multi_attach'))
        self.is_subfolder.set(self.settings.GetSetting('subfolder'))
        self.is_subject.set(self.settings.GetSetting('is_subject'))
        self.is_filename.set(self.settings.GetSetting('is_filename'))
        self.username.set(self.settings.GetSetting('username'))
        self.password.set(self.settings.GetSetting('password'))
        self.url_login.set(self.settings.GetSetting('url_login'))
        self.url_main.set(self.settings.GetSetting('url_main'))
        self.default_subject.set(self.settings.GetSetting('default_subject'))
        self.default_filename.set(self.settings.GetSetting('default_filename'))
        self.overwite_existing.set(self.settings.GetSetting('overwite_existing'))
        self.auto_export.set(self.settings.GetSetting('auto_export'))
        
        self.default_urlLogin = "https://wfm.coach.com/wfm/EmpLogin"
        self.default_urlMain = "https://wfm.coach.com/wfm/dailyview_entry?matrixAction=APPTBOOKINGDTL_ENTRY"

    def create_generalTab(self, parentTab):
        self.lbl_Gen = tk.Label(parentTab, text="Email configuration", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_Gen.grid(row=0, column=0, columnspan=2, sticky='W', padx=1, pady=4)
        self.lbl_NoteGen = tk.Label(parentTab, text="Options in sending crawled data.", fg ='darkgray')
        self.lbl_NoteGen.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=1)
        
        self.chk_isAppend = tk.Checkbutton(parentTab, text="Append crawled data per Activity",variable=self.is_append, onvalue=1, offvalue=0)
        self.chk_isAppend.grid(row=2, column=0, columnspan =3, sticky='W', pady=2)

        self.chk_isSend = tk.Checkbutton(parentTab, text="Send after crawling", variable=self.is_send,onvalue=1, offvalue=0)
        self.chk_isSend.grid(row=3, column=0, columnspan =3,sticky='W', pady=2)

        self.chk_isSubject = tk.Checkbutton(parentTab, text="Default email subject:", variable=self.is_subject,onvalue=1, offvalue=0, command=self.is_subjectChecked)
        self.chk_isSubject.grid(row=4, column=0, sticky='W', pady=2)

        self.txt_subject = tk.Entry(parentTab, textvariable=self.default_subject, state="readonly", width = 40)
        self.txt_subject.grid(row=4, column=1, columnspan =3, sticky="WE", pady=2)

        self.lbl_AttachmentMode = tk.Label(parentTab, text="Email attachment mode", font='Tahoma 8 bold')
        self.lbl_AttachmentMode.grid(row=5, column=0, columnspan=3, sticky='W', padx=1, pady=6)

        self.rbtn_single = tk.Radiobutton(parentTab, text="Attach exported single file",
                                          variable=self.multi_attachments, value=1,
                                          command=self.is_multiAttach)
        self.rbtn_single.grid(row=6, column=0, columnspan=3, sticky='W', padx=5, pady=0)

        self.rbtn_multi = tk.Radiobutton(parentTab, text="Attach all exported file(s) inside folder",
                                         variable=self.multi_attachments, value=2,
                                         command=self.is_multiAttach)
        self.rbtn_multi.grid(row=7, column=0, columnspan=3, sticky='W', padx=5, pady=0)


    def create_exportTab(self, parentTab):
        self.lbl_Exp = tk.Label(parentTab, text="Export configuration", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_Exp.grid(row=0, column=0, columnspan=2, sticky='W', padx=1, pady=4)
        self.lbl_NoteExp = tk.Label(parentTab, text="Options in exporting crawled data.", fg ='darkgray')
        self.lbl_NoteExp.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=1)
        
        self.chk_isDateSubfolder = tk.Checkbutton(parentTab, text="Create Date subfolder",
                                               variable=self.is_subfolder,
                                               onvalue=1, offvalue=0, command=self.is_filenameChecked)
        self.chk_isDateSubfolder.grid(row=2, column=0, columnspan=4, sticky='W', pady=2)

        self.chk_isFilename = tk.Checkbutton(parentTab, text="Filename", variable=self.is_filename,
                                             onvalue=1, offvalue=0, command=self.is_filenameChecked)
        self.chk_isFilename.grid(row=3, column=0, sticky='W', pady=2)

        self.txt_filename = tk.Entry(parentTab, width=40, textvariable=self.default_filename, state="readonly")
        self.txt_filename.grid(row=3, column=1, columnspan=4, sticky="WE", pady=2)

        self.lbl_folder = tk.Label(parentTab, text="Export To:")
        self.lbl_folder.grid(row=4, column=0,  sticky='W', padx=5, pady=2)

        self.txt_folder = tk.Entry(parentTab, width=40, textvariable=self.folder_location,state="readonly")
        self.txt_folder.grid(row=4, column=1, columnspan=4, sticky="WE", pady=2)

        self.img_browse = PhotoImage(file="images/browse.png")
        self.btn_browseFolder = tk.Button(parentTab, text="Browse", image= self.img_browse, compound=LEFT, command=self.getFolder)
        self.btn_browseFolder.grid(row=4, column=5, sticky='W', padx=5, pady=2)

        self.chk_overwiteExisting = tk.Checkbutton(parentTab, text="Overwite existing file if exist",
                                               variable=self.overwite_existing,
                                               onvalue=1, offvalue=0)
        self.chk_overwiteExisting.grid(row=5, column=0, columnspan=4, sticky='W', pady=2)

        self.chk_autoExport = tk.Checkbutton(parentTab, text="Automatic export crawled data",
                                               variable=self.auto_export,
                                               onvalue=1, offvalue=0)
        self.chk_autoExport.grid(row=6, column=0, columnspan=4, sticky='W', pady=2)

        

    def create_sitesTab(self, parentTab):
        self.lbl_WFM = tk.Label(parentTab, text="WFM Authentication", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_WFM.grid(row=0, column=0, columnspan=2, sticky='W', padx=1, pady=4)
        self.lbl_Note = tk.Label(parentTab, text="Credentials use to login WFM site.", fg ='darkgray')
        self.lbl_Note.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=1)
        
        self.lbl_username = tk.Label(parentTab, text="   Username:")
        self.lbl_username.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.txt_username = tk.Entry(parentTab, textvariable=self.username, width=23)
        self.txt_username.grid(row=2, column=1, columnspan=4, sticky="WE", pady=2)

        self.lbl_password = tk.Label(parentTab, text="Password:")
        self.lbl_password.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.txt_password = tk.Entry(parentTab, textvariable=self.password, show=self.bullet, width=23)
        self.txt_password.grid(row=3, column=1, columnspan=4, sticky="WE", pady=2)
        
        self.lbl_Note1 = tk.Label(parentTab, text="A predefined urls use in crawling, enter your url to modified.", fg ='green')
        self.lbl_Note1.grid(row=4, column=0, columnspan=2, sticky='W', padx=5, pady=2)
        
        self.lbl_Login = tk.Label(parentTab, text="Login URL:")
        self.lbl_Login.grid(row=5, column=0,  sticky='W', padx=5, pady=2)

        #self.txt_urlLogin = tk.Entry(parentTab, width=50, justify=LEFT, textvariable=self.url_login)
        #self.txt_urlLogin.grid(row=5, column=1, columnspan=4, sticky="WE", pady=2)
        self.txt_urlLogin = tk.Text(parentTab, height=3, width=38)
        self.txt_urlLogin.grid(row=5, column=1, columnspan=4, sticky="WE", pady=2)
        self.txt_urlLogin.insert(tk.END,self.url_login.get())
        self.lbl_Main = tk.Label(parentTab, text="Main URL:")
        self.lbl_Main.grid(row=6, column=0,  sticky='W', padx=5, pady=2)

        #self.txt_urlMain = tk.Entry(parentTab, width=50, justify=LEFT, textvariable=self.url_main)
        #self.txt_urlMain.grid(row=3, column=1, columnspan=4, sticky="WE", pady=2)
        self.txt_urlMain = tk.Text(parentTab, height=3, width=38)
        self.txt_urlMain.grid(row=6, column=1, columnspan=4, sticky="WE", pady=2)
        self.txt_urlMain.insert(tk.END, self.url_main.get())
        pass

    def create_parserTab(self, parentTab):
        self.lbl_Spacer2 = tk.Label(parentTab,fg="gray", wraplength= 350, justify=LEFT, text="For development purpose only.\nEnter parser (html.parser or lxml) or leave blank if you don't want to set parser.")
        self.lbl_Spacer2.grid(row=0, column=0, columnspan=4,sticky='W', padx=1, pady=4)
        
        self.lbl_parser = tk.Label(parentTab, text="Parser:")
        self.lbl_parser.grid(row=1, column=0, sticky='E', padx=5, pady=2)

        self.txt_parser = tk.Entry(parentTab, textvariable=self.parser, width=23)
        self.txt_parser.grid(row=1, column=1, columnspan=4, sticky="WE", pady=2)

        self.lbl_Ex = tk.Label(parentTab, text="Example ", fg='gray',justify=tk.LEFT)
        self.lbl_Ex.grid(row=2, column=0,  sticky='E', padx=1, pady=1)

        self.lbl_Spacer1 = tk.Label(parentTab, text="html.parser\nlxml", fg='blue',justify=tk.LEFT)
        self.lbl_Spacer1.grid(row=2, column=1, columnspan=4, sticky='W', padx=1, pady=1)

        
        self.chk_isKillProcess = tk.Checkbutton(parentTab, text="Kill Internet Explorer process.",
                                               variable=self.kill_ie,
                                               onvalue=1, offvalue=0)
        self.chk_isKillProcess.grid(row=3, column=0, columnspan=4, sticky='W', pady=2)

        self.chk_isVisible = tk.Checkbutton(parentTab, text="Internet Explorer visiblity during crawling.",
                                               variable=self.is_visible,
                                               onvalue=1, offvalue=0)
        self.chk_isVisible.grid(row=4, column=0, columnspan=4, sticky='W', pady=2)

    def is_multiAttach(self):
        self.settings.SetSettings('multi_attach', self.multi_attachments.get())

    def is_subjectChecked(self):
            checked = self.is_subject.get()
            if checked and checked == 1:
                self.txt_subject['state'] = "normal"
            else:
                self.default_subject.set('')
                self.txt_subject['state'] = "readonly"
            self.settings.SetSettings('is_subject', checked)
            self.settings.SetSettings('default_subject', self.default_subject.get())

    def getFolder(self):
        folder = filedialog.askdirectory(parent=self, initialdir="/",title='Please select a directory where you want to export Crawled Data')
        if self.helper.is_notEmpty(folder):
            self.helper.resolveDirectory(folder)
            self.settings.SetSettings('exportto', folder)
            self.folder_location.set(folder)
    
    def is_filenameChecked(self):
        checked = self.is_filename.get()
        if checked and checked == 1:
            self.txt_filename['state'] = "normal"
        else:
            self.default_filename.set('')
            self.txt_filename['state'] = "readonly"
        self.settings.SetSettings('is_filename', checked)
        self.settings.SetSettings('default_filename', self.default_filename.get())

    def ok(self):
        ul = self.txt_urlLogin.get("1.0","end-1c")
        um = self.txt_urlMain.get("1.0","end-1c")
        if ul.strip() is None:
            ul = self.default_urlLogin
        if um.strip() is None:
            um = self.default_urlMain

        self.settings.SetSettings('send', self.is_send.get())
        self.settings.SetSettings('append', self.is_append.get())
        self.settings.SetSettings('subfolder', self.is_subfolder.get())
        self.settings.SetSettings('exportto', self.folder_location.get())
        self.settings.SetSettings('multi_attach', self.multi_attachments.get())
        self.settings.SetSettings('username', self.username.get())
        self.settings.SetSettings('password', self.password.get())
        self.settings.SetSettings('url_login', ul)
        self.settings.SetSettings('url_main', um)
        self.settings.SetSettings('default_subject', self.default_subject.get())
        self.settings.SetSettings('overwite_existing', self.overwite_existing.get())
        self.settings.SetSettings('auto_export', self.auto_export.get())
        self.settings.SetSettings('parser', self.parser.get())
        self.settings.SetSettings('kill_ie', self.kill_ie.get())
        self.settings.SetSettings('default_subject', self.default_subject.get())
        self.settings.SetSettings('default_filename', self.default_filename.get())
        self.settings.SetSettings('is_subject', self.is_subject.get())
        self.settings.SetSettings('is_filename', self.is_filename.get())
        self.settings.SetSettings('is_visible', self.is_visible.get())
        
        self.destroy()




import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from Settings import Settings
from StorageDb import StorageDb
from Helper import Helper
from CalendarDialog  import CalendarDialog
from AppointmentHelper import AppointmentHelper
import re
import time
import datetime
import calendar


WORKSPACES = 'workspaces'

class ConfigCrawlDialog(simpledialog.Dialog):
    def body(self, master):
        self.parent = master
        self.frame = tk.Frame(self.parent, width=500)
        self.resizable(width=False, height=False)
        self.iconbitmap('tarsier.ico')
        
        self.storage = StorageDb('wfm.sqlite')
        self.appt_helper = AppointmentHelper()
        self.settings = Settings()
        self.helper = Helper()

        self.init_variables()
        self.tab_control = ttk.Notebook(self.parent)
        self.img_tab = {}
        self.tabs = ["Appointment Booking Detail","Authentication"]
        for tab in self.tabs:
            tabPage = ttk.Frame(self.tab_control)   # first page, which would get widgets gridded into it
            self.img_tab[tab] = PhotoImage(file=str("images/%s.png" % tab.replace(' ','')))
            self.tab_control.add(tabPage, text= tab, image =self.img_tab[tab], compound=LEFT)
            if tab is 'Authentication':
                self.create_authTab(tabPage)
            else:
                self.create_filterTab(tabPage)
        self.tab_control.pack(expand=1, fill="both")  # Pack to make visible
                
        self.frame.pack(expand=1, fill="both",padx=8, pady=5)

    def init_variables(self):
        self.kill_ie = tk.IntVar()
        self.is_visible = tk.IntVar()
        self.company_id = tk.StringVar()
        self.dispatcher_id = tk.StringVar()
        self.status = tk.StringVar()
        self.appt_company_id = tk.StringVar()
        self.appt_dispatcher_id = tk.StringVar()
        self.appt_status = tk.StringVar()
        self.selected_dateFrom = tk.StringVar()
        self.selected_dateTo = tk.StringVar()
        
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.bullet = "*"  # specifies bullet character
        
        self.is_visible.set(self.settings.GetSetting('is_visible'))
        self.kill_ie.set(self.settings.GetSetting('kill_ie'))
        self.company_id.set(self.settings.GetSetting('company_id'))
        self.dispatcher_id.set(self.settings.GetSetting('dispatcher_id'))
        self.status.set(self.settings.GetSetting('status'))
        self.username.set(self.settings.GetSetting('username'))
        self.password.set(self.settings.GetSetting('password'))
        
        self.year = time.localtime()[0]
        self.month = time.localtime()[1]
        self.day = time.localtime()[2]
        self.strdate = (str(self.month).zfill(2) + "/" + str(self.day).zfill(2) + "/" + str(self.year))
        self.selected_dateFrom.set(self.strdate)
        self.selected_dateTo.set(self.strdate)
        
        date_from = self.settings.GetSetting('selected_dateFrom').strip()
        date_to = self.settings.GetSetting('selected_dateTo').strip()
        if date_from and date_from.strip():
            self.selected_dateFrom.set(date_from)
        if date_to and date_to.strip():
            self.selected_dateTo.set(date_to)

        
        self.companies_id = []
        self.dispachers_id = []
        self.appt_activity = []
        self.appt_statuses = []
        
        rows_dis = self.storage.GetResults('select * from dispatchers where active =1')
        if len(rows_dis) >0 :
            for row in rows_dis:
                self.dispachers_id.append(row['value'] +' - '+row['description'])

        rows_comps = self.storage.GetResults('select * from companies where active =1')
        if len(rows_comps) >0 :
            for row in rows_comps:
                self.companies_id.append(row['value'] +' - '+row['description'])

        rows_stats = self.storage.GetResults('select * from status where active =1')
        if len(rows_stats) >0 :
            for row in rows_stats:
                self.appt_statuses.append(row['value'] +' - '+row['description'])

        rows_acts = self.storage.GetResults('select * from activities where active =1')
        if len(rows_acts) >0 :
            for row in rows_acts:
                self.appt_activity.append(row['value'])

        self.img_dateTo = PhotoImage(file="images/date_to.png")
        self.img_dateFrom = PhotoImage(file="images/date_from.png")

    def create_filterTab(self, tabPage):
        self.lbl_AttachmentMode = tk.Label(tabPage, text="Appointment Search Options", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_AttachmentMode.grid(row=0, column=0, columnspan=5, sticky='W', padx=1, pady=6)
        self.lbl_Note = tk.Label(tabPage, text="Please provide your desired appointment search filter", fg ='green')
        self.lbl_Note.grid(row=1, column=0, columnspan=5, sticky='W', padx=5, pady=2)
        
        self.lbl_companyId = tk.Label(tabPage, text="Company ID:")
        self.lbl_companyId.grid(row=2, column=0, sticky='W', padx=5, pady=2)

        self.cbox_companyId = ttk.Combobox(tabPage, textvariable=self.company_id, state="readonly", width = 50)
        self.cbox_companyId.bind('<Return>')
        self.cbox_companyId['values'] = self.companies_id 
        #self.cbox_companyId.current(0) # select index 0 by default
        self.cbox_companyId.grid(row=2, column=1, columnspan=5, sticky="W", pady=3)

        self.lbl_dispatcherId = tk.Label(tabPage, text="Dispatcher ID:")
        self.lbl_dispatcherId.grid(row=3, column=0, sticky='W', padx=5, pady=2)

        self.cbox_dispatcherId = ttk.Combobox(tabPage, textvariable=self.dispatcher_id, state="readonly", width = 60)
        self.cbox_dispatcherId.bind('<Return>')
        self.cbox_dispatcherId['values'] = self.dispachers_id
        #self.cbox_dispatcherId.current(0) # select index 0 by default
        self.cbox_dispatcherId.grid(row=3, column=1, columnspan=5, sticky="W", pady=3)
        
        self.lbl_apptStatus = tk.Label(tabPage, text="Appt Status:")
        self.lbl_apptStatus.grid(row=4, column=0, sticky='E', padx=5, pady=2)

        self.cbox_apptStatus = ttk.Combobox(tabPage, textvariable=self.status, state="readonly")
        self.cbox_apptStatus.bind('<<ComboboxStatus>>')
        self.cbox_apptStatus['values'] = self.appt_statuses
        #self.cbox_apptStatus.current(0) # select index 0 by default
        self.cbox_apptStatus.grid(row=4, column=1, columnspan=5, sticky="WE", pady=2)

        self.lbl_Spacer1 = tk.Label(tabPage, text="")
        self.lbl_Spacer1.grid(row=5, column=0, columnspan=5, sticky='E', padx=5, pady=4)

        self.lbl_dateFrom = tk.Label(tabPage, text="Date From:")
        self.lbl_dateFrom.grid(row=6, column=0, sticky='E', padx=5, pady=2)

        self.txt_dateFrom = tk.Entry(tabPage, textvariable=self.selected_dateFrom, state="readonly", width=14)
        self.txt_dateFrom.grid(row=6, column=1,  sticky="WE", pady=2)

        self.btn_dateFrom = tk.Button(tabPage, image = self.img_dateFrom, text="...", command=lambda: self.getCalendarDate("from"))
        self.btn_dateFrom.grid(row=6, column=2, sticky='W', padx=5, pady=2)

        self.lbl_dateTo = tk.Label(tabPage, text="Date To:")
        self.lbl_dateTo.grid(row=6, column=3, sticky='E', padx=5, pady=2)

        self.txt_dateTo = tk.Entry(tabPage, textvariable=self.selected_dateTo, state="readonly", width=14)
        self.txt_dateTo.grid(row=6, column=4,  sticky="WE", pady=2)

        self.btn_dateTo = tk.Button(tabPage, image = self.img_dateTo,  text="...", command=lambda: self.getCalendarDate("to"))
        self.btn_dateTo.grid(row=6, column=5, sticky='W', padx=5, pady=2)

    def create_authTab(self, tabPage):
        self.lbl_WFM = tk.Label(tabPage, text="WFM Authentication", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_WFM.grid(row=0, column=0, columnspan=2, sticky='W', padx=1, pady=4)
        self.lbl_Note = tk.Label(tabPage, text="Credentials use to login WFM site.", fg ='darkgray')
        self.lbl_Note.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=1)
        
        self.lbl_username = tk.Label(tabPage, text="   Username:")
        self.lbl_username.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.txt_username = tk.Entry(tabPage, textvariable=self.username, width=40)
        self.txt_username.grid(row=2, column=1, columnspan=4, sticky="WE", pady=2)

        self.lbl_password = tk.Label(tabPage, text="Password:")
        self.lbl_password.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.txt_password = tk.Entry(tabPage, textvariable=self.password, show=self.bullet, width=40)
        self.txt_password.grid(row=3, column=1, columnspan=4, sticky="WE", pady=2)
                
        self.lbl_Other = tk.Label(tabPage, text="Other crawler options", font='Tahoma 8 bold', fg = 'gray')
        self.lbl_Other.grid(row=4, column=0, columnspan=2, sticky='W', padx=1, pady=4)
        self.lbl_OtherNote = tk.Label(tabPage, text="Please provide some of ccrawling options.", fg ='darkgray')
        self.lbl_OtherNote.grid(row=5, column=0, columnspan=2, sticky='W', padx=5, pady=1)

        
        self.chk_isKillProcess = tk.Checkbutton(tabPage, text="Kill opened Internet Explorer process.",
                                               variable=self.kill_ie,
                                               onvalue=1, offvalue=0)
        self.chk_isKillProcess.grid(row=6, column=0, columnspan=4, sticky='W', pady=2)

        self.chk_isVisible = tk.Checkbutton(tabPage, text="Internet Explorer visiblity during crawling.",
                                               variable=self.is_visible,
                                               onvalue=1, offvalue=0)
        self.chk_isVisible.grid(row=7, column=0, columnspan=4, sticky='W', pady=2)


    def getCalendarDate(self,date_state):
        datee = datetime.datetime.strptime(self.selected_dateTo.get(), "%m/%d/%Y")
        if (date_state == "from"):
            datee = datetime.datetime.strptime(self.selected_dateTo.get(), "%m/%d/%Y")
            
        #cd = CalendarDialog(self.parent,title="Calendar", year= str(datee.year), month= str(datee.month))
        cd = CalendarDialog(self.parent,title="Calendar")
        result = cd.result
        if (result and result != ''):
            if (date_state == "from"):
                self.selected_dateFrom.set(result.strftime("%m/%d/%Y"))
            else:
                self.selected_dateTo.set(result.strftime("%m/%d/%Y"))

    def getCurrentDate(self,):
        return time.strftime("%Y-%m-%d")
    
    def getCurrentTime(self,):
        return time.strftime("%I:%M:%S %p")

    def ok(self):
        self.settings.SetSettings('username', self.username.get())
        self.settings.SetSettings('password', self.password.get())
        self.settings.SetSettings('selected_dateFrom', self.selected_dateFrom.get())
        self.settings.SetSettings('selected_dateTo', self.selected_dateTo.get())
        self.settings.SetSettings('is_visible', self.is_visible.get())
        self.settings.SetSettings('kill_ie', self.kill_ie.get())

        self.appt_company_id = self.appt_helper.get_value(self.company_id.get())
        self.appt_dispatcher_id = self.appt_helper.get_value(self.dispatcher_id.get())
        self.appt_status = self.appt_helper.get_value(self.cbox_apptStatus.get()).replace('#','Any')
        
        if self.helper.is_notEmpty(self.appt_company_id) and self.helper.is_notEmpty(self.appt_dispatcher_id)  and self.helper.is_notEmpty(self.appt_status) :
            self.settings.SetSettings('appt_company_id', self.appt_company_id)
            self.settings.SetSettings('appt_dispatcher_id', self.appt_dispatcher_id)
            self.settings.SetSettings('appt_status', self.appt_status)
            self.settings.SetSettings('company_id', self.company_id.get())
            self.settings.SetSettings('dispatcher_id', self.dispatcher_id.get())
            self.settings.SetSettings('status', self.status.get())
            ws = []
            ws.append(self.appt_company_id)
            ws.append(self.appt_dispatcher_id)
            ws.append(self.appt_status)
            ws.append((self.selected_dateFrom.get() + "-" + self.selected_dateTo.get()).replace("/", "."))
            work_name =  "wfm-" + " ".join(ws)
            code = self.helper.non_alphanumeric(work_name).lower()

            content_val = {}
            content_val['name'] = work_name
            content_val['count'] = '0'
            content_val['details'] = self.appt_helper.get_currentDate()
            content_val['date_from'] = self.selected_dateFrom.get()
            content_val['date_to'] = self.selected_dateTo.get()
            content_val['company_id'] = self.appt_company_id
            content_val['dispatcher_id'] = self.appt_dispatcher_id
            content_val['status'] = self.appt_status
            content_val['code'] = code

            self.add_workspace(content_val, code) # add new workspace
            self.storage.CreateWFMTable(code)     # create table for WFM
            self.storage.CreateLinksTable(code+'_links')     # create table for WFM links
        
            self.settings.SetSettings('workspace_name', work_name)
            self.settings.SetSettings('wfm_table', code)
            self.destroy()

    def add_workspace(self, content_val, code):
        if self.storage.IsExist(WORKSPACES, 'code', code):
            self.storage.UpdateParameterized(WORKSPACES, content_val, "code='" + code + "'")
        else:
            self.storage.InsertParameterized(WORKSPACES, content_val)


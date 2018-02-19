import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from Settings import Settings
from StorageDb import StorageDb
from AppointmentInput  import AppointmentInput
from Helper import Helper

class DispatcherDialog(simpledialog.Dialog):
    def body(self, master):
        self.parent = master
        self.frame = tk.Frame(self.parent)
        self.resizable(width=False, height=False)
        self.iconbitmap('tarsier.ico')
		
        self.storage = StorageDb('wfm.sqlite')
        self.settings = Settings()
        self.helper = Helper()
        self.init_variables()

        self.tab_control = ttk.Notebook(self.parent)
        self.img_tab = {}
        self.tabs = ["Appointment Booking Detail"]
        for tab in self.tabs:
            tabPage = ttk.Frame(self.tab_control)   # first page, which would get widgets gridded into it
            self.img_tab[tab] = PhotoImage(file=str("images/%s.png" % tab.replace(' ','')))
            self.tab_control.add(tabPage, text= tab, image =self.img_tab[tab], compound=LEFT)
            if tab is 'Authentication':
                #self.create_authTab(tabPage)
                pass
            else:
                self.create_dispatcherTab(tabPage)
                pass

        self.init_dispatchers()

        self.btn_add = tk.Button(self.frame, text='Add', image= self.img_add,compound= LEFT, command=self.add_dispatcher)
        self.btn_add.grid(row=0, column=0, sticky="E", padx=2, pady=2)
        
        self.btn_edit = tk.Button(self.frame, text='Edit', image= self.img_edit,compound= LEFT,command=self.edit_dispatcher)
        self.btn_edit.grid(row=0, column=2, sticky="E", padx=2, pady=2)

        self.btn_delete = tk.Button(self.frame, text='Delete', image= self.img_remove,compound= LEFT,command=self.delete_dispatcher)
        self.btn_delete.grid(row=0, column=3, sticky="E", padx=2, pady=2)

        self.tab_control.pack(expand=1, fill="both")
        self.frame.pack(expand=1, fill="both")
        
    def init_variables(self):
        self.value = tk.StringVar()
        self.description = tk.StringVar()
        self.active = tk.IntVar()
        self.selected_id = tk.StringVar()
        
        self.img_add = PhotoImage(file="images/list_add.png") 
        self.img_edit = PhotoImage(file="images/list_edit.png") 
        self.img_remove = PhotoImage(file="images/list_remove.png") 
        self.img_warning = PhotoImage(file="images/warning.png") 
        self.img_active = PhotoImage(file="images/yes.png") 
        self.img_notactive = PhotoImage(file="images/no.png") 
        
        self.DISPATCHERS = 'dispatchers'
        self.TABLE = 'dispatchers'
        selected_table = self.settings.GetSetting('selected_table') # get selected id from settings
        if self.helper.is_notEmpty(selected_table):
            self.TABLE = selected_table

        pass

    def create_dispatcherTab(self, tabPage):
        self.treeAppointment = ttk.Treeview(tabPage, selectmode='browse')
        verticalScroll = ttk.Scrollbar(tabPage, orient='vertical', command=self.treeAppointment.yview)
        verticalScroll.pack(side='right', fill='y')
        horScroll = ttk.Scrollbar(tabPage, orient='horizontal', command=self.treeAppointment.xview)
        horScroll.pack(side='bottom', fill='x')
        
        self.treeAppointment.configure(yscrollcommand=verticalScroll.set)
        self.treeAppointment.configure(xscrollcommand=horScroll.set)

        self.treeAppointment['columns'] = ('value','description', 'active')
        #self.treeAppointment['show'] = 'headings'
        self.treeAppointment.heading("#0", text='id', anchor='w')
        #self.treeAppointment.column("#0", anchor="w", width=20)
        self.treeAppointment.heading('value', text='Value')
        self.treeAppointment.column('value', anchor='w')
        self.treeAppointment.heading('description', text='Description')
        self.treeAppointment.column('description', anchor='w')
        self.treeAppointment.heading('active', text='Active')
        self.treeAppointment.column('active', anchor='center', width=20)
        self.treeAppointment.pack(expand=1, fill='both')
        pass

    def init_dispatchers(self):
        self.treeAppointment.delete(*self.treeAppointment.get_children())
        rows = self.storage.FetchAllRows(self.TABLE)
        if len(rows) > 0:
            for row in rows:
                img = self.img_notactive
                if row['active'] ==1:
                    img = self.img_active
                self.treeAppointment.insert('', 'end',  image =  img, text=row['id'], values= (row['value'],row['description'],row['active']))
        else:
            self.treeAppointment.insert('', 'end', image =  self.img_warning, text='', values= ('No data found!','',''))
        self.treeAppointment.bind('<ButtonRelease-1>', self.itemClicked)
        self.selected_id.set('') # clear selected id
        self.settings.SetSettings('selected_id', '') # clear selected id from settings
        pass
    

    def itemClicked(self, event):
        #print('Item clicked....')
        curItem = self.treeAppointment.focus()
        self.selected_id.set(self.treeAppointment.item(curItem, "text"))
        #print(self.selected_id.get())
        self.settings.SetSettings('selected_id', self.selected_id.get())
       # print(self.treeAppointment.item(curItem))
       # print(self.treeAppointment.item(curItem, "text"))
       # print(self.treeAppointment.item(curItem, "values")[0])

    def add_dispatcher(self):
        self.settings.SetSettings('action_button', 'ADD') # set an action button that in dialog
        d = AppointmentInput(self.parent,title='Add '+ self.TABLE.title())
        if d.is_OK.get() is True:
            print ('OK........')
            if self.helper.is_notEmpty(d.value.get()) and self.helper.is_notEmpty(d.description.get()):
                content_val = {}
                content_val['value'] = self.helper.trim_spaces(d.value.get())
                content_val['description'] = self.helper.trim_spaces(d.description.get())
                content_val['active'] = 1
                if self.storage.IsExist(self.TABLE, 'value', d.value.get().strip()):
                    self.storage.UpdateParameterized(self.TABLE, content_val, "value='" + d.value.get().strip() + "'")
                else:
                    self.storage.InsertParameterized(self.TABLE, content_val)
                self.init_dispatchers()
        pass
    def edit_dispatcher(self):
        self.settings.SetSettings('action_button', 'EDIT') # set an action button that in dialog
        if self.helper.is_notEmpty(self.selected_id.get()):
            d = AppointmentInput(self.parent,title='Edit '+ self.TABLE.title())
            if self.helper.is_notEmpty(d.value.get()) and self.helper.is_notEmpty(d.description.get()):
                content_val = {}
                content_val['value'] = self.helper.trim_spaces(d.value.get())
                content_val['description'] = self.helper.trim_spaces(d.description.get())
                content_val['active'] =d.active.get()
                self.storage.UpdateParameterized(self.TABLE, content_val, "id=" + str(self.selected_id.get()))
                self.init_dispatchers()
        pass
    
    def delete_dispatcher(self):
        self.settings.SetSettings('action_button', 'DELETE') # set an action button that in dialog
        pass

    def get_selectedId(self):
        return self.selected_id.get()
        

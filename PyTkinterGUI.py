__author__ = 'Tarsier'
try:
    from Tkinter import *
    import ttk
    import tkFileDialog
except:
    from tkinter import *
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import simpledialog
    from tkinter import messagebox

import os
import time
import datetime
from threading import Thread
from Settings import Settings
from StorageDb import StorageDb
from Helper import Helper
from ServerDialog import ServerDialog
from RecipientDialog import RecipientDialog
from OptionsDialog import OptionsDialog
from ConfigCrawlDialog import ConfigCrawlDialog
from DispatcherDialog  import DispatcherDialog
from AboutDialog import AboutDialog
from Components import Components

# declare constant tables
DISPATCHERS = 'dispatchers'
COMPANIES = 'companies'
WORKSPACES = 'workspaces'
RECIPIENTS = 'recipients'
SETTINGS = 'settings'
ERRORS = 'errors'
AUTH = 'auth'
TABLE_ALLDATA = 'all_data'

#libraries for crawling WFM data
#it helps some function of IEC.py
import pythoncom
from win32com.client import Dispatch
pythoncom.CoInitialize()


class Application(Frame):
    WFM_TABLE = 'all_data'
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.init_externalClasses()
        self.init_globalVariables()
        self.init_settings()
        self.init_uiImages()
        self.parent = parent
        
        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)
        self.parent.bind("<Destroy>", lambda e: self.onExit)

        self.initMenubar()
        self.initToolbar()
        self.initPanedWindow()
        self.create_StatusBar()
        #self.LoadTable()
        self.parent.config(menu=self.menubar)
        self.pack()

        self.start_dataThread()
        
        if self.is_loading == False:
            self.treeview.bind('<ButtonRelease-1>', self.itemClicked)

        #self.grid(sticky = (N,S,W,E))
        #self.parent.grid_rowconfigure(0, weight = 1)
        #self.parent.grid_columnconfigure(0, weight = 1)
    def start_dataThread(self):
        try:
            self.thread = Thread(target=self.load_dataTable, name = str(datetime.datetime.now()))
            self.is_loading = True
            self.progressbar.pack(side=LEFT)
            # change the cursor
            self.parent.config(cursor="wait")
            # force Tk to update
            self.parent.update()

            # start the thread and progress bar
            self.thread.start()
            self.progressbar.start()
            # check in 50 milliseconds if the thread has finished
            self.parent.after(50, self.loading_completed)
        except:
            pass

    def init_externalClasses(self):
        self.storage = StorageDb('wfm.sqlite')
        self._helper = Helper()
        self.settings = Settings()
        #self.component = Components()

    def init_settings(self):
        self.kill_ie.set(self.settings.GetSetting('kill_ie'))
        self.is_visible.set(self.settings.GetSetting('is_visible'))
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
        self.workspace_name.set(self.settings.GetSetting('workspace_name'))
        self.wfm_table.set(self.settings.GetSetting('wfm_table'))
        self.date_from.set(self.settings.GetSetting('selected_dateFrom').strip())
        self.date_to.set(self.settings.GetSetting('selected_dateTo').strip())
        self.set_WFMTable(self.wfm_table.get()) # set wfm table to all variable handle with it
        #self.set_WFMTable(TABLE_ALLDATA) # set wfm table to all variable handle with it

        self.date_filter = []
        rows = self.storage.GetResults('select distinct(CabinetNo) from %s order by CabinetNo asc' % (self.wfm_table.get()))
        if len(rows) >0:
            for r in rows:
                self.date_filter.append(r['CabinetNo'])
        
    def init_globalVariables(self):
        self.images_tools = {}
        self.images_menu = {}
        self.images_navs = {}
        self.filename = StringVar()
        self.wfm_table = StringVar()
        self.image_folder = StringVar()
        self.search_keyword = StringVar()
        self.lbl_status = StringVar()
        self.lbl_wfmTable = StringVar()
        self.filter = StringVar()
        self.count_page = StringVar()
        self.rows_count = StringVar()
        self.workspace_name = StringVar()
        
        self.progress = IntVar()
        self.progress.set(0)
        self.progress_maximum = IntVar()
        self.progress_maximum.set(100)

        # Settings variables
        self.is_append = IntVar()
        self.is_send = IntVar()
        self.is_subject = IntVar()
        self.is_subfolder = IntVar()
        self.is_filename = IntVar()
        self.multi_attachments = IntVar()
        self.overwite_existing = IntVar()
        self.auto_export = IntVar()
        self.default_subject = StringVar()
        self.default_filename = StringVar()
        self.folder_location = StringVar()
        self.url_login = StringVar()
        self.url_main = StringVar()
        self.username = StringVar()
        self.password = StringVar()
        self.parser = StringVar()
        self.date_from = StringVar()
        self.date_to = StringVar()
        self.kill_ie = IntVar()
        self.is_visible = IntVar()
        self.bullet = "*"  # specifies bullet character
        
        self.is_loading = False

        self.openfdialog_filter = 'Open supported files'
        self.savefdialog_filter = 'Save As created file'
        self.menus = {"File": ["New","Start Crawl","Refresh","-","Save","Save As...","-","Print Preview","Preferences...","-","Exit"],
                 "Appointment": ["Companies","Dispatchers","Status"],
                 "Options": ["Server Connection","Recipients","-","Preferences"],
                 "View": ["check#Workspace","check#Toolbar","check#Statusbar","-","check#Large Icons"],
                 "Help": ["Documentation","About"]
                 }
        self.tools = {"File": ["New","StartCrawl","Refresh","All","-","Save","SaveAs","PrintPreview","-"],
                 "Appointment": ["Companies","Dispatchers","Status","-"],
                 "Options": ["ServerConnection","Recipients","Preferences","-"],
                 "Help": ["Documentation","About"]
                 }
        self.navs = ["nav_first","nav_previous","nav_next","nav_last"]

        
        self.img_workpaces = PhotoImage(file="images/Workpaces.png")
        self.img_errors = PhotoImage(file="images/CrawlErrors.png") 
        self.img_find = PhotoImage(file="images/Find.png") 
        self.img_filter = PhotoImage(file="images/filter.png") 
        self.img_filter_advanced = PhotoImage(file="images/filter_advanced.png") 
        self.img_works = PhotoImage(file="images/works.png") 
        self.img_error = PhotoImage(file="images/error.png") 
        self.img_warning = PhotoImage(file="images/warning.png") 


    def init_uiImages(self):
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.image_folder = os.path.join(self.image_path,'16')
        if False:
            self.image_folder = os.path.join(self.image_path,'32')
        print(self.image_folder)
    
    def new_Crawl(self):
        pass
    def doClickEvent(self, index, tag):
        if self.is_loading == True: # block click event if loading data in process
            return

        if tag.find('check#') != -1:
            print('index: %s label: %s' % (index,tag))
            print(self.check[index].get())
        else:
            if tag is 'Open':
                self.filename = filedialog.askopenfilename(initialdir = "/",title = self.openfdialog_filter ,filetypes = (("Supported Files (*.py)","*.py"),("All Files","*.*")))
                print(self.filename)
            elif tag.find('Server') != -1:
                s = ServerDialog(self.parent, title=tag)
            elif tag is 'SaveAs':
                self.filename = filedialog.asksaveasfilename(initialdir = "/",title = self.savefdialog_filter,filetypes = (("Supported Files (*.py)","*.py"),("All Files","*.*")))
            elif tag is 'Recipients':
                r = RecipientDialog(self.parent,title="Email Addresses ")
            elif tag is 'New':
                c = ConfigCrawlDialog(self.parent,title="New Crawl")
                self.init_settings()
                self.init_workspaces()
            elif tag.find('Preferences') != -1:
                o = OptionsDialog(self.parent,title=tag)
            elif tag.find('About') != -1:
                a = AboutDialog(self.parent,title=tag)
            elif tag.find('Dispatchers') != -1:
                self.settings.SetSettings('selected_table', 'dispatchers') # set an action button that in dialog
                d = DispatcherDialog(self.parent,title=tag)
            elif tag.find('Companies') != -1:
                self.settings.SetSettings('selected_table', 'companies') # set an action button that in dialog
                d = DispatcherDialog(self.parent,title=tag)
            elif tag.find('Refresh') != -1:
                self.init_workspaces()
                self.start_dataThread()
            elif tag.find('All') != -1:
                res = messagebox.askquestion('Load All Crawled Data', 'This may take a few time.\nAre you sure you want to load all crawled data from WFM?')
                if res == 'yes':
                    self.set_WFMTable(TABLE_ALLDATA)
                    self.start_dataThread()
            elif tag.find('Status') != -1:
                self.settings.SetSettings('selected_table', 'status') # set an action button that in dialog
                d = DispatcherDialog(self.parent,title=tag)

            elif tag.find('Exit') != -1:
                self.onExit()
            elif tag.find('StartCrawl') != -1:
                if self.kill_ie.get()== 1:
                    self.process.kill_process('iexplore.exe')

                self.crawlDialog = CrawlerDialog(self.parent)  # init GUI
                #self.crawler = Crawler(self.crawlDialog) #init Controller
                #self.crawler.startCrawler()
                
            else:
                print('doClickEvent  index: %s label: %s' % (index,tag))

    def initMenubar(self):
        images_folder_format = "images/16/%s-%s.png"
        self.menubar = Menu(self.parent)
        filemenu = Menu(self.menubar, tearoff=0)

       
        self.check_menus = []
        self.check = {}
        index = 0
        for key, value in self.menus.items():
            topMenu = Menu(self.menubar, tearoff=0)
            for menu in value:
                if menu is "-":
                    topMenu.add_separator()
                else:
                    if menu.startswith('check#'):
                        trim_name = menu.replace('check#','')
                        self.check[index] = StringVar() #handles check state dynamically by check menu index
                        topMenu.add_checkbutton(label=trim_name,  variable=self.check[index], onvalue=1, offvalue=0, command=(lambda tag=menu, i=index :self.doClickEvent(i,tag)))
                        self.check_menus.append((index,trim_name))
                        index += 1
                    else:
                        self.images_menu[menu] = PhotoImage(file=str(images_folder_format % (key, self._helper.non_alphanumeric(menu))))
                        topMenu.add_command(label=menu, compound=LEFT,image=self.images_menu[menu],command=lambda tag=menu :self.doClickEvent(0,tag))
            self.menubar.add_cascade(label=key, menu=topMenu)

    def initToolbar(self):
        self.toolbar = Frame(self.parent, bd=1, relief=RAISED)
        images_folder_format = "images/16/%s-%s.png"
        if False:
            images_folder_format = "images/32/%s-%s.png"

        for key, value in self.tools.items():
            for tool in value:
                self.images_tools[tool] = PhotoImage(file=str(images_folder_format % (key, tool)))
                self.btn_tool = Button(self.toolbar, image=self.images_tools[tool], text=tool,relief=FLAT, justify=CENTER ,command=lambda tag=tool :self.doClickEvent(0,tag))
                self.btn_tool.image = self.images_tools[tool]
                if tool is "-":
                    self.btn_tool.configure(state=NORMAL)
                self.btn_tool.pack(side=LEFT, padx=2, pady=2)
                #toolbars.append((tool, btn_tool))
        self.toolbar.pack(side=TOP, fill=X)

    def initPanedWindow(self):
        #self.paned_window = PanedWindow(bg="green")
        self.paned_window = PanedWindow()
        self.paned_window.pack(fill=BOTH, expand=1)

        self.leftPaneComponents()
         
        self.top_paned_window = PanedWindow(self.paned_window, orient=VERTICAL)
        self.paned_window.add(self.top_paned_window)
       
        top_frame = ttk.Frame(self.top_paned_window)
        nav_buttons = ['<<', '<', '>', '>>']
        
        #for b in nav_buttons:
        for b in self.navs:
            self.images_navs[b] = PhotoImage(file=str('images/%s.png' % (b)))
            btn_nav = Button(top_frame, image=self.images_navs[b], text=b,relief=GROOVE, justify=CENTER ,command=lambda tag=b :self.doClickEvent(0,tag))
            #btn_nav = Button(top_frame, text= b,relief=GROOVE)
            btn_nav.pack(side=LEFT, padx=0, pady=0)
        top_frame.pack(fill=X, padx=200)
        self.top_paned_window.add(top_frame)
        cbox_CountPage = ttk.Combobox(top_frame, textvariable=self.count_page, state="readonly",width = 4)
        cbox_CountPage.bind('<Return>')
        cbox_CountPage['values'] = ('All','10', '25', '50', '75', '100', '150', '200')
        cbox_CountPage.current(0)
        cbox_CountPage.pack(side=LEFT, padx=1, pady=1)
        lbl_Search = Label(top_frame, text="Search:")
        lbl_Search.pack(side=LEFT, padx=1, pady=1)
        txt_Search = Entry(top_frame, text='Keyword', textvariable=self.search_keyword)
        txt_Search.pack(side=LEFT, padx=1, pady=1)
        btn_Search = Button(top_frame, text='Find', image= self.img_find, relief=GROOVE, justify=CENTER ,command=lambda tag='Find' :self.doClickEvent(0,tag))
        btn_Search.pack(side=LEFT, padx=1, pady=1)

        lbl_Filter = Label(top_frame, text="Filter:")
        lbl_Filter.pack(side=LEFT, padx=1, pady=1)
        cbox_Filter = ttk.Combobox(top_frame, textvariable=self.filter, state="readonly",width = 10)
        cbox_Filter.bind('<Return>')
        cbox_Filter['values'] = self.date_filter
        #cbox_Filter.current(0)
        cbox_Filter.pack(side=LEFT, padx=1, pady=1)
        #cbox_Filter.grid(row=1, column=1, columnspan=7, sticky="WE", pady=3)
        btn_Filter = Button(top_frame, text='Filter', image= self.img_filter, relief=GROOVE, justify=CENTER ,command=lambda tag='Filter' :self.doClickEvent(0,tag))
        btn_Filter.pack(side=LEFT, padx=1, pady=1)
        btn_FilterAdvanced = Button(top_frame, text='Filter Advanced', image= self.img_filter_advanced, relief=GROOVE, justify=CENTER ,command=lambda tag='Filter Advanced' :self.doClickEvent(0,tag))
        btn_FilterAdvanced.pack(side=LEFT, padx=1, pady=1)
    
        label = Label(top_frame,textvariable=self.rows_count, bd=1, relief=FLAT, anchor=W)
        self.rows_count.set('15 of 40')
        label.pack(side=LEFT,fill=X)

        self.initTable()
        
       
    def create_StatusBar(self):
        self.status_frame = Frame(self.parent, bd=1, relief=GROOVE)
        self.status_frame.pack(fill=X)
        label = Label(self.status_frame,textvariable=self.lbl_status, anchor=W)
        self.lbl_status.set('Ready...')
        label.pack(side=LEFT)
        self.progressbar = ttk.Progressbar(self.status_frame, orient='horizontal',  variable=self.progress, maximum=self.progress_maximum.get(),length=200)
        #self.progressbar.pack(expand=True, fill=BOTH, side=TOP)
        self.progressbar.pack(side=LEFT)
        #self.progress_load.start(0)
       
        lbl_TableDummy = Label(self.status_frame,text='Workspace:' , anchor=W)
        lbl_TableDummy.pack(side=LEFT)
        lbl_Table = Label(self.status_frame,text='Table:' ,textvariable=self.lbl_wfmTable, anchor=E, fg = 'blue')
        self.lbl_wfmTable.set(self.wfm_table.get())
        lbl_Table.pack(side=LEFT)

    def leftPaneComponents(self):
        tabControl = ttk.Notebook(self.paned_window, width=200)          # Create Tab Control
        tabPage1 = ttk.Frame(tabControl)            # Create a tab
        tabPage2 = ttk.Frame(tabControl)            # Create a tab
        
        self.treeWorkspace = ttk.Treeview(tabPage1, selectmode='browse')
        verticalScroll = ttk.Scrollbar(tabPage1, orient='vertical', command=self.treeWorkspace.yview)
        verticalScroll.pack(side='right', fill='y')
        horScroll = ttk.Scrollbar(tabPage1, orient='horizontal', command=self.treeWorkspace.xview)
        horScroll.pack(side='bottom', fill='x')
        
        self.treeWorkspace.configure(yscrollcommand=verticalScroll.set)
        self.treeWorkspace.configure(xscrollcommand=horScroll.set)

        self.treeWorkspace['columns'] = ('count', 'details')
        #self.treeWorkspace['show'] = 'headings'
        self.treeWorkspace.heading("#0", text='Name', anchor='w')
        #self.treeWorkspace.column("#0", anchor="w", width=40)
        self.treeWorkspace.heading('count', text='Count')
        self.treeWorkspace.column('count', stretch ='yes', anchor='center', width=14)
        self.treeWorkspace.heading('details', text='Details')
        self.treeWorkspace.column('details', anchor='center', width=20)

        self.init_workspaces()
        self.treeWorkspace.pack(expand=1, fill='both')
        
        tabPage1.pack(expand=1,fill="both")  # Pack to make visible
        tabPage2.pack(fill="both")  # Pack to make visible
        tabControl.add(tabPage1, text='Workspaces', image =self.img_workpaces, compound=LEFT)      # Add the tab
        tabControl.add(tabPage2, text='Error Links', image =self.img_errors, compound=LEFT)   # Add the tab
        tabControl.pack(expand=1, fill="both")  # Pack to make visible
        self.paned_window.add(tabControl)

    def init_workspaces(self):
        self.treeWorkspace.delete(*self.treeWorkspace.get_children())
        rows = self.storage.FetchAllRows(WORKSPACES)
        if len(rows) > 0:
            for row in rows:
                self.treeWorkspace.insert('', 'end',image= self.img_works, text=row['name'], values= (row['count'],row['details']))
            
            self.treeWorkspace.bind("<Double-1>", self.onDoubleClickWorkspace)
        else:
            self.treeWorkspace.insert('', 'end',image=self.img_error, text='No data found!', values= ('',''))
        pass

    def initTable(self):
        self.treeview = ttk.Treeview(self.top_paned_window)
       
        #cols = self.storage.FetchAllColumns(TABLE_ALLDATA)
        cols = self.storage.FetchAllColumns(self.WFM_TABLE)
        self.columns = []
        if len(cols) > 0:
            for c in cols:
                col_name = c[1].strip()
                if col_name != 'id' and col_name != 'JobActivityList':
                    #print(col_name)
                    self.columns.append(col_name)
            self.treeview['columns'] = self.columns
            self.treeview.heading("#0", text='ID')
            self.treeview.column("#0", anchor='w', width= 50)
            for c in self.columns:
                #self.treeview.heading(c, text=c.title())
                self.treeview.heading(c, text=c)
                self.treeview.column(c, anchor='w')


       
        ysb = Scrollbar(orient=VERTICAL, command= self.treeview.yview)
        xsb = Scrollbar(orient=HORIZONTAL, command= self.treeview.xview)
        self.treeview['yscroll'] = ysb.set
        self.treeview['xscroll'] = xsb.set

        # add tree and scrollbars to frame
        self.treeview.grid(in_=self.top_paned_window, row=0, column=0, sticky=(N, S, W, E),pady=50)
        ysb.grid(in_=self.top_paned_window, row=0, column=1, sticky="NS")
        xsb.grid(in_=self.top_paned_window, row=3, column=0, sticky="EW")

        self.top_paned_window.add(self.treeview)
        self.top_paned_window.rowconfigure(0, weight=1)
        self.top_paned_window.columnconfigure(0, weight=1)

    def load_dataTable(self):
        
        self.treeview.delete(*self.treeview.get_children())
        #rows = self.storage.FetchAllRows(TABLE_ALLDATA)
        rows = self.storage.FetchAllRows(self.WFM_TABLE)
        self.progress_maximum.set(len(rows)) # set maximum value of progressbar
        self.progressbar['maximum'] = len(rows)
        i = 1
        if len(rows) > 0:
            for row in rows:
                values = []
                id = row['id']
                for col in self.columns:
                    values.append(row[col])
                #time.sleep(0.1)
                self.progress.set(i)
                self.lbl_status.set('Loading ...%s of %s ' % (i, self.progress_maximum.get()))
                self.treeview.insert("", "end", text=id, values=values)
                #del values[:]
                #del values
                i +=1
           
        #self.treeview.bind('<ButtonRelease-1>', self.itemClicked)

        

    def loading_completed(self):
        if self.thread.is_alive():
            # if the thread is still alive check again in 50 milliseconds
            self.parent.after(50, self.loading_completed)
        else:
            # if thread has finished stop and reset everything
            self.progressbar.stop()
            self.progressbar.pack_forget()
            #self.browse_button.config(state="enabled")
            self.parent.config(cursor="")
            self.parent.update()
            self.is_loading = False
            self.lbl_status.set('Ready...')
            self.treeview.bind('<ButtonRelease-1>', self.onItemClicked)
            self.treeview.bind("<Double-1>", self.onDoubleClick)

    def onItemClicked(self, event):
        if self.is_loading == True: # do nothing if data loading is still in progress
            return
        try:
            curItem = self.treeview.focus()
            print(self.treeview.item(curItem))
            print(self.treeview.item(curItem, "text"))
            print(self.treeview.item(curItem, "values")[0])
        except:
            pass
    def onDoubleClick(self, event):
        if self.is_loading == True: # do nothing if data loading is still in progress
            return
        item = self.treeview.selection()[0]
        print("you clicked on", self.treeview.item(item,"text"))

    def onDoubleClickWorkspace(self, event):
        if self.is_loading == True: # do nothing if data loading is still in progress
            return
        item = self.treeWorkspace.selection()[0]
        ws = self._helper.non_alphanumeric( self.treeWorkspace.item(item,"text")).lower()
        if self._helper.is_notEmpty(ws):
            print("you clicked on", ws)
            self.set_WFMTable(ws)
            self.start_dataThread() # start loading all data from selected workspace
        
    def set_WFMTable(self, table):
        self.wfm_table.set(table)
        self.WFM_TABLE = table
        self.settings.SetSettings('wfm_table', table)
        self.lbl_wfmTable.set(table)

    def onExit(self):
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.parent.destroy()
        except:
            pass

def main():
    root = Tk()
    style = ttk.Style()
    #print (style.theme_names())
    style.theme_use('winnative') #set default theme
    root.geometry("860x400+100+100")
    app = Application(root)
    app.master.title("Py GUI Sample using TKinter")
    app.master.iconbitmap('tarsier.ico')

    if 'win' not in sys.platform:
        style.theme_use('clam')
    #root.bind('<Escape>', lambda e: root.destroy()) #enable close if ESCAPE key was pressed
    root.mainloop()

if __name__ == '__main__':
    main()

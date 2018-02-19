
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from Settings import Settings
from ArpTable import ArpTable

class ServerDialog(simpledialog.Dialog):
    def body(self, master):
        frame = tk.Frame(master, width=500)
        self.resizable(width=False, height=False)
        self.iconbitmap('tarsier.ico')      

        self.settings = Settings()
        self.arp = ArpTable()

        self.bullet = "*"  # specifies bullet character
        self.hostname = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.database = tk.StringVar()
        
        self.hostname.set(self.settings.GetSetting('server_hostname'))
        self.username.set(self.settings.GetSetting('server_username'))
        self.password.set(self.settings.GetSetting('server_password'))
        self.database.set(self.settings.GetSetting('server_database'))

        self.frame_server = tk.LabelFrame(frame, text="Server Authentication")
        self.frame_server.grid(row=0, column=0, sticky='W')
        self.frame_server.grid(padx=5, pady=5)

        self.lbl_Spacer1 = tk.Label(self.frame_server, text="",width=4)
        self.lbl_Spacer1.grid(row=0, column=4,columnspan=5, sticky='W', padx=5, pady=2)

        self.lbl_hostname = tk.Label(self.frame_server, text="   Hostname:")
        self.lbl_hostname.grid(row=1, column=0, sticky='E', padx=5, pady=2)

        self.cbox_hostname = ttk.Combobox(self.frame_server, textvariable=self.hostname, state="readonly", width=28)
        self.cbox_hostname.bind('<Return>')
        self.cbox_hostname['values'] = self.arp.get_ips('192')
        self.cbox_hostname.current(0)
        self.cbox_hostname.grid(row=1, column=1,columnspan=2, sticky="W", pady=2)

        #self.txt_hostname = tk.Entry(self.frame_server, textvariable=self.hostname, width=28)
        #self.txt_hostname.grid(row=1, column=1,columnspan=2, sticky="W", pady=2)

        self.lbl_username = tk.Label(self.frame_server, text="   Username:")
        self.lbl_username.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.txt_username = tk.Entry(self.frame_server, textvariable=self.username, width=31)
        self.txt_username.grid(row=2, column=1, columnspan=2,sticky="W", pady=2)

        self.lbl_password = tk.Label(self.frame_server, text="Password:")
        self.lbl_password.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.txt_password = tk.Entry(self.frame_server, textvariable=self.password, show=self.bullet, width=31)
        self.txt_password.grid(row=3, column=1, columnspan=2,sticky="W", pady=2)

        self.lbl_database = tk.Label(self.frame_server, text="Database:")
        self.lbl_database.grid(row=4, column=0, sticky='E', padx=5, pady=2)

        self.txt_database = tk.Entry(self.frame_server, textvariable=self.database, width=31)
        self.txt_database.grid(row=4, column=1, columnspan=2, sticky="W", pady=2)

        self.lbl_Spacer1 = tk.Label(self.frame_server, text="",width=4)
        self.lbl_Spacer1.grid(row=5, column=4,columnspan=5, sticky='W', padx=5, pady=2)

        frame.pack(expand =1, fill='both')



    def ok(self):
        self.settings.SetSettings('server_hostname', self.hostname.get())
        self.settings.SetSettings('server_username', self.username.get())
        self.settings.SetSettings('server_password', self.password.get())
        self.settings.SetSettings('server_database', self.database.get())
        self.destroy()


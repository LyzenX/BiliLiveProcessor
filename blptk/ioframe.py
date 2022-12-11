from blptk.tkmodules import tk, ttk, tku

class IoFrame(ttk.LabelFrame):

    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent, text='输入', padding=2)
        self.pack(fill=tk.BOTH)
        self.grid_columnconfigure(1, weight=1)
        self.init_widgets()

    def init_widgets(self):
        self.init_input_filename_widgets()
        self.init_analyse_widgets()
        tku.add_border_space(self, 1, 1)

    def init_input_filename_widgets(self):
        strvar = tk.StringVar()
        label = ttk.Label(self, text='工作目录：')
        entry = ttk.Entry(self, textvariable=strvar)
        button = ttk.Button(self, text='浏览', width=6)

        label.grid(row=0, column=0, sticky=tk.E)
        entry.grid(row=0, column=1, sticky=tk.EW)
        button.grid(row=0, column=2, sticky=tk.W)

        strvar.set('')
        button['command'] = self.on_input_filename_button_clicked

        self.input_filename_strvar = strvar

    def init_analyse_widgets(self):
        button = ttk.Button(self, text='分析', width=6)

        button.grid(row=3, column=2, sticky=tk.W)

        button['command'] = self.on_analyse_button_clicked
        self.convert_button = button

    def on_input_filename_button_clicked(self):
        strvar = self.input_filename_strvar
        tku.on_filedialog(self, strvar=strvar, method='load')()

    def on_analyse_button_clicked(self):
        self.event_generate('<<AnalyseButtonClicked>>')

    def values(self):
        return self.input_filename_strvar.get().strip()

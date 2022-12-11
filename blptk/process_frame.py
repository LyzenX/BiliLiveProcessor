from blptk.tkmodules import tk, ttk, tku


class ProcessFrame(ttk.LabelFrame):

    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent, text='输出', padding=2)
        self.pack(fill=tk.BOTH)
        self.grid_columnconfigure(1, weight=1)
        self.init_widgets()

    def init_widgets(self):
        self.init_process_widgets()
        self.init_advanced_options()
        self.init_horizontal_process_widgets()
        self.init_vertical_process_widgets()
        tku.add_border_space(self, 1, 1)

    def init_process_widgets(self):
        button = ttk.Button(self, text='生成处理文件', width=6)

        button.grid(row=1, column=1, sticky=tk.EW)

        button['command'] = self.on_process_button_clicked
        self.convert_button = button

    def init_advanced_options(self):
        # label = ttk.Label(self, text='高级选项(慎重选择)')
        # label.grid(row=2, column=1, sticky=tk.EW)
        intvar = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            self, text='高级选项(慎重选择)', variable=intvar, command=self.on_advanced_options_clicked)
        checkbutton.grid(row=2, column=1, sticky=tk.EW, columnspan=3)
        self.advanced_options_intvar = intvar

    def init_horizontal_process_widgets(self):
        button = ttk.Button(self, text='强制生成横屏', width=6)

        button.grid(row=3, column=1, sticky=tk.EW)
        button.grid_remove()

        button['command'] = self.on_horizontal_button_clicked
        self.horizontal_button = button

    def init_vertical_process_widgets(self):
        button = ttk.Button(self, text='强制生成竖屏', width=6)

        button.grid(row=4, column=1, sticky=tk.EW)
        button.grid_remove()

        button['command'] = self.on_vertical_button_clicked
        self.vertical_button = button

    def on_advanced_options_clicked(self):
        if self.advanced_options_intvar.get() == 1:
            self.horizontal_button.grid()
            self.vertical_button.grid()
        else:
            self.horizontal_button.grid_remove()
            self.vertical_button.grid_remove()

    def on_process_button_clicked(self):
        self.event_generate('<<ProcessButtonClicked>>')

    def on_horizontal_button_clicked(self):
        self.event_generate('<<HorizontalButtonClicked>>')

    def on_vertical_button_clicked(self):
        self.event_generate('<<VerticalButtonClicked>>')

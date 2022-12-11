from blptk.tkmodules import tk, ttk, tku


class OptionsFrame(ttk.LabelFrame):

    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent, text='选项', padding=2)
        self.pack(fill=tk.BOTH)
        self.grid_columnconfigure(1, weight=1)
        self.init_widgets()

    def init_widgets(self):
        self.init_no_danmu_button()
        self.init_danmu_button()
        self.init_small_danmu_button()
        self.init_bell_button()
        tku.add_border_space(self, 1, 1)

    def init_no_danmu_button(self):
        intvar = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            self, text='输出无弹幕版', variable=intvar)
        checkbutton.grid(row=1, column=0, sticky=tk.W, columnspan=3)
        intvar.set(1)
        self.no_danmu_intvar = intvar

    def init_danmu_button(self):
        intvar = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            self, text='输出有弹幕版', variable=intvar)
        checkbutton.grid(row=2, column=0, sticky=tk.W, columnspan=3)
        intvar.set(1)
        self.danmu_intvar = intvar

    def init_small_danmu_button(self):
        intvar = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            self, text='横屏时输出小弹幕版', variable=intvar)
        checkbutton.grid(row=3, column=0, sticky=tk.W, columnspan=3)
        intvar.set(1)
        self.small_danmu_intvar = intvar

    def init_bell_button(self):
        intvar = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            self, text='完成时播放声音', variable=intvar)
        checkbutton.grid(row=4, column=0, sticky=tk.W, columnspan=3)
        intvar.set(1)
        self.bell_intvar = intvar

    def values(self):
        return dict(
            no_danmu=self.no_danmu_intvar.get() == 1,
            danmu=self.danmu_intvar.get() == 1,
            small_danmu=self.small_danmu_intvar.get() == 1,
            bell=self.bell_intvar.get() == 1,
        )

import sys

import blptk.processor
from blptk import analyser
from blptk.ioframe import IoFrame
from blptk.option_frame import OptionsFrame
from blptk.process_frame import ProcessFrame
from blptk.tkmodules import tk, ttk, tku
from blptk.loggingframe import LoggingFrame


class Application(ttk.Frame):
    def __init__(self):
        ttk.Frame.__init__(self, None, border=2)
        self.pack(fill=tk.BOTH, expand=True)
        self.init_win()
        self.videos = []
        self.analysed_path = None
        self.output_method = -1
        self.fast_no_danmu = False

    def init_win(self):
        self.init_top()
        self.init_rootpane()
        self.init_left_frame()
        self.init_right_frame()
        if sys.platform.startswith('win'):
            self.topwin.withdraw()
            tku.move_to_screen_center(self.topwin)
            self.topwin.deiconify()

    def init_top(self):
        self.topwin = self.winfo_toplevel()
        self.topwin.title('BiliLiveProcessor')
        self.topwin.protocol('WM_DELETE_WINDOW', self.quit)

    def init_rootpane(self):
        self.rootpane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.rootpane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def init_left_frame(self):
        frame = ttk.Frame(self)
        self.logging_frame = LoggingFrame(frame)
        frame.grid_columnconfigure(1, weight=1)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.rootpane.add(frame)
        self.set_log("请选择工作目录\n点击右方“浏览”按钮\n在弹出的窗口中将目录定位到录播目录下并点击选择按钮\n然后点击分析")

    def init_right_frame(self):
        frame = ttk.Frame(self)
        self.io_frame = IoFrame(frame)
        self.options_frame = OptionsFrame(frame)
        self.process_frame = ProcessFrame(frame)
        self.io_frame.bind('<<AnalyseButtonClicked>>',
                           self.on_analyse_button_clicked)
        self.process_frame.bind('<<ProcessButtonClicked>>',
                                self.on_process_button_clicked)
        self.process_frame.bind('<<HorizontalButtonClicked>>',
                                self.on_horizontal_button_clicked)
        self.process_frame.bind('<<VerticalButtonClicked>>',
                                self.on_vertical_button_clicked)
        frame.grid_columnconfigure(1, weight=1)
        frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.rootpane.add(frame)

    def insert_log(self, string):
        self.logging_frame.write(string)

    def set_log(self, string):
        self.logging_frame.set(string)

    def get_options(self):
        return self.options_frame.values()

    def on_analyse_button_clicked(self, event):
        input_dir = self.io_frame.values()
        analyser.analyse(input_dir, self)

    def on_process_button_clicked(self, event):
        blptk.processor.generate(self)

    def on_horizontal_button_clicked(self, event):
        blptk.processor.generate(self, output_method=1)

    def on_vertical_button_clicked(self, event):
        blptk.processor.generate(self, output_method=0)

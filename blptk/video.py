class Video:
    def __init__(self, flv, xml, date, time):
        self.flv = flv
        self.video_name = flv[:flv.rindex('.')]
        self.xml = xml
        self.date = date
        self.time = time
        self.columns = None
        self.rows = None
        self.fps = None
        self.duration = None

from reportlab.lib.pagesizes import LETTER, inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


class Canvas(canvas.Canvas):
    metadata: None

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.w, self.h = LETTER

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if (self._pageNumber > 1):
                self.drawHeader(page_count)
            canvas.Canvas.showPage(self)

        self.setAuthor(self.metadata["author"])
        self.setProducer(self.metadata["producer"])
        self.setCreator(self.metadata["creator"])
        self.setSubject(self.metadata["subject"])
        self.setTitle(self.metadata["title"])
        self.setKeywords(self.metadata["keywords"])
        canvas.Canvas.save(self)

    def drawHeader(self, page_count):
        page = "Página %s de %s" % (self._pageNumber, page_count)
        self.saveState()
        # Header images
        self.drawImage("assets/images/logrhythm.png", (self.w - 5) - (inch * 8), self.h -
                       50, width=100, height=20, preserveAspectRatio=True, mask="auto")
        self.drawImage("assets/images/netready-horizontal.png", self.w - (inch * 2), self.h - 50,
                       width=100, height=30, preserveAspectRatio=True, mask="auto")
        # Lines
        self.setFillColor(HexColor(0x8C8984))
        self.setStrokeColor(HexColor(0x8C8984))
        self.setLineWidth(1 / 2)
        self.line(30, 740, self.w - 50, 740)
        self.line(66, 78, self.w - 66, 78)

        # Text footer
        # self.setFillColor(HexColor(0x8C8984))
        self.setFillColor(HexColor(0x000000))
        self.setFont("Arial-Narrow", 10)
        self.drawString(self.w - 128, 65, page)
        self.restoreState()

        self.saveState()
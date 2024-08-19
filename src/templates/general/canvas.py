from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class Canvas(canvas.Canvas):
    metadata: dict

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.w, self.h = LETTER

    def draw_images(self):
        self.drawImage("./assets/images/netready-h.png", 2.50 * cm, self.h - 1.75 * cm,
                       width=6.096 * cm,
                       height=1.27 * cm, preserveAspectRatio=True, mask="auto")

    def showPage(self):
        if self._pageNumber > 1:
            self.draw_images()

        canvas.Canvas.showPage(self)

    def save(self):
        if self.metadata:
            self.setAuthor(self.metadata.get("author"))
            self.setProducer(self.metadata.get("producer"))
            self.setCreator(self.metadata.get("creator"))
            self.setSubject(self.metadata.get("subject"))
            self.setTitle(self.metadata.get("title"))
            self.setKeywords(self.metadata.get("keywords"))
        
        canvas.Canvas.save(self)

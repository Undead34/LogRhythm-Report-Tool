# ReportLab Libraries
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import utils


class Report(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        SimpleDocTemplate.__init__(self, *args, **kwargs)

    def beforePage(self):
        ctx = self.canv
        w, h = LETTER
        img = utils.ImageReader("assets/images/background.png")
        ctx.saveState()
        ctx.drawImage(img, 0, 310, width=w, height=h, preserveAspectRatio=True)
        ctx.restoreState()

        if (self.page == 1):
            img = utils.ImageReader("assets/images/water.png")
            ctx.saveState()
            ctx.drawImage(img, w / 4, h / 4, width=w/2, height=h/2,
                          preserveAspectRatio=True, mask="auto")
            ctx.restoreState()

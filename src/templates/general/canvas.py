from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from .theme import Theme

class Canvas(canvas.Canvas):
    theme: Theme = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def draw_header(self):
        pass

    def draw_footer(self):
        pass

    def draw_cover(self):
        self.saveState()
        width, height = self.theme.pagesize
        _, margin_top, _, _ = self.theme.page_margins
    
        image_height = 4.95 * cm
        y_position = height - margin_top - image_height
    
        self.drawImage(
            "./assets/images/NetReady.jpg",
            0,  # X-axis
            y_position,  # Y-axis
            width=width,
            height=image_height,
            preserveAspectRatio=False,
            mask="auto"
        )

    def showPage(self):
        if self.getPageNumber() > 1:
            self.draw_header()
            self.draw_footer()
        else:
            self.draw_cover()

        canvas.Canvas.showPage(self)
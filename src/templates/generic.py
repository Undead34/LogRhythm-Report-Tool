from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen.canvas import Canvas
from src.utils import ElementList

class GenericTheme:
    def __init__(self) -> None:
        pass

class GenericTemplate:
    def __init__(self, output_path: str, metadata: dict, theme: GenericTheme, canvas: Canvas, document=None) -> None:
        self.metadata = metadata
        self.document = document if document else SimpleDocTemplate(output_path, pagesize=LETTER)
        self.width, self.height = self.document.pagesize
        self.elements = ElementList()
        self.theme = theme()
        self.canvasmaker = canvas

    def build(self):
        try:
            if self.canvasmaker:
                self.document.multiBuild(self.elements, canvasmaker=self.canvasmaker)
            else:
                raise RuntimeError("The canvasmaker was not initialized so the program cannot compile the report.")
        finally:
            pass
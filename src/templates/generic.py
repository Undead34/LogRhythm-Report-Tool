from abc import ABC, abstractmethod

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from src.utils import ElementList

class GenericTheme(ABC):
    pagesize: tuple = None
    page_margins: tuple = None

    def __init__(self) -> None:
        pass

    @abstractmethod
    def apply(self, elements: ElementList):
        pass

class GenericTemplate:
    def __init__(self, output_path: str, metadata: dict, theme: GenericTheme, canvas: Canvas, document=None) -> None:
        self.metadata = metadata
        self.theme: GenericTheme = theme()
        
        # Handle None case for page_margins
        if self.theme.page_margins is None:
            self.theme.page_margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # Default margins

        self.document = document if document else SimpleDocTemplate(
            output_path, 
            pagesize=self.theme.pagesize or LETTER, 
            leftMargin=self.theme.page_margins[0], 
            topMargin=self.theme.page_margins[1], 
            rightMargin=self.theme.page_margins[2], 
            bottomMargin=self.theme.page_margins[3]
        )
        self.width, self.height = self.document.pagesize
        self.elements = ElementList()
        self.canvasmaker = canvas
        self.canvasmaker.theme = self.theme

    def build(self):
        try:
            if not self.canvasmaker:
                raise RuntimeError("The canvasmaker was not initialized so the program cannot compile the report.")
            self.document.multiBuild(self.elements, canvasmaker=self.canvasmaker)
        except Exception as e:
            print(f"An error occurred while building the document: {e}")
        finally:
            # Perform any necessary cleanup here
            pass
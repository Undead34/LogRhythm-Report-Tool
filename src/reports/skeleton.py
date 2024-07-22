# ReportLab Libraries
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import LETTER

from src.utils import ElementList
from src.themes.theme import Theme

class Report():
    def __init__(self, output) -> None:
        """
        Inicializa una instancia de la clase Report.

        Args:
            output: Salida para el informe.
            metadata: Metadatos para el informe.
        """
        self.theme = Theme()
        self.template = SimpleDocTemplate(output, pagesize=LETTER,
                                 leftMargin=self.theme.leftMargin,
                                 rightMargin=self.theme.rightMargin,
                                 topMargin=self.theme.topMargin,
                                 bottomMargin=self.theme.bottomMargin)

        # Init Properties
        self.width, self.height = LETTER
        self.elements = ElementList()
        self.canvasmaker = None

    def load_template(self, template):            
        self.elements += template.elements
        self.canvasmaker = template.canvasmaker

    def build(self):
        """
            Método para construir el PDF utilizando todos los elementos agregados al informe.
        """
        if self.canvasmaker:
            self.template.multiBuild(self.elements, canvasmaker=self.canvasmaker)
        else:
            raise RuntimeError("The canvasmaker was not initialized so the program cannot compile the report.")
# ReportLab Libraries
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm

from .template import Template, Canvas, Theme
from utils import ElementList
from .elastic import Package

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import MSQLServer


class Report():
    """
    Clase para construir un informe PDF.

    Attributes:
        metadata: Metadatos para el informe.
        packages: Lista de paquetes para el informe.
        template: Plantilla para el informe.
        elements: Lista de elementos en el informe.
        width: Ancho del informe.
        height: Altura del informe.
        theme: Tema del informe.
        components: Componentes del informe.
    """

    def __init__(self, packages: list[Package], database: 'MSQLServer', output, metadata) -> None:
        """
        Inicializa una instancia de la clase Report.

        Args:
            packages: Lista de paquetes para el informe.
            output: Salida para el informe.
            metadata: Metadatos para el informe.
        """
        self.metadata = metadata
        self.packages = packages
        self.database = database

        self.leftMargin = self.rightMargin = 2.5 * cm
        self.topMargin = self.bottomMargin = 2 * cm

        self.template = Template(output, pagesize=LETTER,
                                 leftMargin=self.leftMargin,
                                 rightMargin=self.rightMargin,
                                 topMargin=self.topMargin,
                                 bottomMargin=self.bottomMargin)

        # Init Properties
        self.width, self.height = LETTER
        self.elements = ElementList()
        self.theme = Theme()

        Canvas.metadata = metadata

    def build(self):
        """
            Método para construir el PDF utilizando todos los elementos agregados al informe.
        """
        self.template.multiBuild(self.elements, canvasmaker=Canvas)

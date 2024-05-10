# ReportLab Libraries
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER, inch


from .template import Template, Canvas, Theme
from .elastic import Package
from .charts import Charts


class Report():
    def __init__(self, packages: list[Package], output, metadata) -> None:
        self.metadata = metadata
        self.packages = packages
        self.template = Template(output, pagesize=LETTER)

        # Init Properties
        self.elements = []
        self.width, self.height = LETTER
        self.styleSheet = getSampleStyleSheet()
        self.theme = Theme()
        Canvas.metadata = metadata

    def build(self):
        self.template.multiBuild(self.elements, canvasmaker=Canvas)

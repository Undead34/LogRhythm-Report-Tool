# ReportLab Libraries
from reportlab.platypus import PageBreak, Image, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Line, Drawing
from reportlab.platypus import SimpleDocTemplate
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.pdfbase import pdfmetrics

# Libraries
import shutil
import os


from .theme import Theme, ParagraphStyles
from .canvas import Canvas
from utils import constants

try:
    for f in constants.FONTS:
        pdfmetrics.registerFont(TTFont(f[0], f[1]))

    os.makedirs(constants.CHARTS_DIR, exist_ok=True)
    shutil.rmtree(constants.CHARTS_DIR)
    os.makedirs(constants.CHARTS_DIR, exist_ok=True)
except:
    print("The error occurred when trying to load the fonts and/or create the necessary folders.")
    exit(1)


class Template(SimpleDocTemplate):
    def __init__(self, *args, **kwargs) -> None:
        SimpleDocTemplate.__init__(self, *args, **kwargs)

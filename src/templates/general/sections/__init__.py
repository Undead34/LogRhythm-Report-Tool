from reportlab.platypus import Paragraph
from reportlab.lib.units import cm

from src.utils import ElementList

def cover_page() -> ElementList:
    elements = ElementList()

    elements += Paragraph("Cover")

    return elements
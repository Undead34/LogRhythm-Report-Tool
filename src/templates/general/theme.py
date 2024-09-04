import os
import shutil
from typing import List, Union, Any

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.utils.constants import CHARTS_DIR
from src.utils import ElementList, Element
from src.templates.generic import GenericTheme
from .text_styles import TEXT_STYLES

from reportlab.platypus import Paragraph

TElementList = List[Union[Element, str, Any]]

class Theme(GenericTheme):
    pagesize: tuple = LETTER
    page_margins: tuple = (2.5 * cm, 2 * cm, 2.5 * cm, 2 * cm) # left, top, right, bottom
    
    def __init__(self) -> None:
        super().__init__()

        self.fonts = [
            ["OpenSans-Regular", "./assets/fonts/OpenSans-Regular.ttf"],
            ["OpenSans-Bold", "./assets/fonts/OpenSans-Bold.ttf"],
            ["Conthrax", "./assets/fonts/Conthrax.ttf"],

            # Arial Narrow Font
            ["Arial-Narrow", "./assets/fonts/Arial Narrow.ttf"],
            ["Arial-Narrow-Italic", "./assets/fonts/Arial Narrow Italic.ttf"],
            ["Arial-Narrow-Bold", "./assets/fonts/Arial Narrow Bold.ttf"],
            ["Arial-Narrow-Bold-Italic", "./assets/fonts/Arial Narrow Bold Italic.ttf"]
        ]

        self._register_fonts()

    def _get_text_style(self, style: str) -> ParagraphStyle:
        return TEXT_STYLES.get(style, None)

    def apply(self, elements: 'TElementList'):
        for i, element in enumerate(elements):
            if isinstance(element, Element):
                if "paragraph" in element.className:
                    element.className.remove("paragraph")
                    style = self._get_text_style(element.className[0])
                    elements[i] = element.render(style)
            else:
                pass

        return elements

    def _register_fonts(self):
        try:
            for name, path in self.fonts:
                pdfmetrics.registerFont(TTFont(name, path))

            os.makedirs(CHARTS_DIR, exist_ok=True)
            shutil.rmtree(CHARTS_DIR)
            os.makedirs(CHARTS_DIR, exist_ok=True)
        except Exception as e:
            print(f"Error loading fonts or creating folders: {e}")
            exit(1)



import os
import shutil
from enum import Enum
from typing import List, Union, Any

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.utils.constants import CHARTS_DIR
from src.utils import ElementList, Element
from src.templates.generic import GenericTheme

TElementList = List[Union[Element, str, Any]]

class FontSize(Enum):
    SMALL = 8
    MEDIUM = 10
    LARGE = 12
    XLARGE = 14
    XXLARGE = 16
    XXXLARGE = 18

class FontFamily(Enum):
    OPEN_SANS = "OpenSans"
    CONTHRAX = "Conthrax"
    ARIAL_NARROW = "Arial-Narrow"

class FontStyle(Enum):
    REGULAR = "Regular"
    BOLD = "Bold"
    ITALIC = "Italic"
    BOLD_ITALIC = "Bold-Italic"

class ParagraphStyle(Enum):
    TITLE = "Title"
    SUBTITLE = "Subtitle"
    HEADING = "Heading"
    SUBHEADING = "Subheading"
    BODY = "Body"
    CAPTION = "Caption"
    LIST = "List"

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

    def apply(self, elements: 'TElementList'):
        for element in elements:
            if isinstance(element, Element):
                if element.className == "Paragraph":
                    # Apply style here
                    pass
            else:
                pass

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
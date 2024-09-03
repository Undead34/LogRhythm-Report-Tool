import os
import shutil
from enum import Enum

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.utils.constants import CHARTS_DIR
from src.templates.generic import GenericTheme

class Theme(GenericTheme):
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
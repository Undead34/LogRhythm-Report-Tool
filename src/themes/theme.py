from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER

from enum import Enum
import shutil
import os

from src.utils.constants import FONTS, CHARTS_DIR


class ParagraphStyles(Enum):
    TEXT_NORMAL = 'Text-Normal'
    TEXT_BOLD = 'Text-Bold'
    TEXT_GRAPHIC = 'Text-Graphic'
    TITLE_1 = 'Title-1'
    TITLE_2 = 'Title-2'
    TITLE_3 = 'Title-3'
    TABLE_HEADER = 'Table-Header'
    TABLE_HEADER_CONTENT = 'Table-Header-Content'
    TEXT_ITALIC = 'Text-Italic'
    LIST = 'List'

class Theme():
    def __init__(self) -> None:
        self.style_sheet = getSampleStyleSheet()

        self.colors = {
            'orange': HexColor(0xF96611),
            'yellow': HexColor(0xF9A40E),
            'blue': HexColor(0x4AAEC9),
            'table_blue': HexColor(0xC5E1FF),
            'dark_blue': HexColor(0x195C74),
            'light_blue': HexColor(0x3796BF),
            'gray': HexColor(0x8C8984),
            'black': HexColor(0x000000),
            'white': HexColor(0xFFFFFF)
        }

        self.leftMargin = self.rightMargin = 2.5 * cm
        self.topMargin = self.bottomMargin = 2 * cm
        self.page_width, self.page_height = LETTER

        self._register_fonts()
        self._initialize_paragraph_styles()

    def _register_fonts(self):
        try:
            for f in FONTS:
                pdfmetrics.registerFont(TTFont(f[0], f[1]))

            os.makedirs(CHARTS_DIR, exist_ok=True)
            shutil.rmtree(CHARTS_DIR)
            os.makedirs(CHARTS_DIR, exist_ok=True)
        except:
            print("The error occurred when trying to load the fonts and/or create the necessary folders.")
            exit(1)

    def _initialize_paragraph_styles(self):
        styles = self.style_sheet

        styles.add(ParagraphStyle(ParagraphStyles.TEXT_NORMAL.value,
                                  fontName="Arial-Narrow",
                                  fontSize=12,
                                  spaceAfter=12,
                                  alignment=TA_JUSTIFY,
                                  leading=13.8
                                  ))

        styles.add(ParagraphStyle(ParagraphStyles.TEXT_BOLD.value,
                                  fontName="Arial-Narrow-Bold",
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value],
                                  ))

        styles.add(ParagraphStyle(ParagraphStyles.TABLE_HEADER.value,
                                  fontName="Arial-Narrow-Bold",
                                  fontSize=12,
                                  alignment=TA_CENTER,
                                  textColor=self.colors['white'],
                                  leading=13.8
                                  ))

        styles.add(ParagraphStyle(ParagraphStyles.TABLE_HEADER_CONTENT.value,
                                  alignment=TA_CENTER,
                                  spaceAfter=0,
                                  leftIndent=0,
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value],
                                  ))

        styles.add(ParagraphStyle(name=ParagraphStyles.TEXT_GRAPHIC.value,
                                  fontName='Arial-Narrow-Bold-Italic',
                                  fontSize=11,
                                  textColor=self.colors['black'],
                                  spaceBefore=6,
                                  spaceAfter=14,
                                  firstLineIndent=1 * cm,
                                  alignment=TA_CENTER))

        styles.add(ParagraphStyle(name=ParagraphStyles.TEXT_ITALIC.value,
                                  fontName='Arial-Narrow-Italic',
                                  fontSize=11,
                                  textColor=self.colors['black'],
                                  alignment=TA_CENTER))

        styles.add(ParagraphStyle(name=ParagraphStyles.TITLE_1.value,
                                  fontName='Arial-Narrow-Bold',
                                  fontSize=18,
                                  textColor=self.colors['light_blue'],
                                  spaceBefore=30,
                                  spaceAfter=24,
                                  leftIndent=0,
                                  firstLineIndent=17.9,
                                  alignment=TA_CENTER,
                                  leading=20.7))

        styles.add(ParagraphStyle(name=ParagraphStyles.TITLE_2.value,
                                  parent=styles[ParagraphStyles.TITLE_1.value],
                                  alignment=TA_JUSTIFY))

        styles.add(ParagraphStyle(name=ParagraphStyles.TITLE_3.value,
                                  parent=styles[ParagraphStyles.TITLE_1.value],
                                  leftIndent=0,
                                  firstLineIndent=28.9))

        styles.add(ParagraphStyle(name=ParagraphStyles.LIST.value,
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value],
                                  spaceAfter=6,
                                  spaceBefore=6,
                                  leading=13.8))

    def get_style(self, style_name: ParagraphStyles | str) -> ParagraphStyle:
        if isinstance(style_name, str):
            return self.style_sheet.get(style_name)
        else:
            return self.style_sheet.get(style_name.value)

    def replace_bold_with_font(self, text):
        import re
        return re.sub(r'\*\*(.*?)\*\*', r'<font face="Arial-Narrow-Bold">\1</font>', text)
    
    def replace_italic_with_font(self, text):
        import re
        return re.sub(r'__(.*?)__', r'<font face="Arial-Narrow-Italic">\1</font>', text)

    def replace_color_with_font(self, text, color):
        import re
        return re.sub(r'\[\[(.*?)\]\]', rf'<font color="{color}">\1</font>', text)

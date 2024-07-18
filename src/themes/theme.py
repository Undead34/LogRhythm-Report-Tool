from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.platypus import TableStyle
from reportlab.lib.pagesizes import LETTER
from enum import Enum
import shutil
import os
from src.utils.constants import FONTS, CHARTS_DIR


class ParagraphStyles(Enum):
    TEXT_NORMAL = 'Text-Normal'
    SUB_TEXT_NORMAL = 'Sub-Text-Normal'
    TEXT_BOLD = 'Text-Bold'
    TEXT_GRAPHIC = 'Text-Graphic'
    TITLE_1 = 'Title-1'
    TITLE_2 = 'Title-2'
    TITLE_3 = 'Title-3'
    TABLE_HEADER = 'Table-Header'
    TABLE_HEADER_CONTENT = 'Table-Header-Content'
    TEXT_ITALIC = 'Text-Italic'
    LIST = 'List'
    SUB_LIST = 'Sub-List'
    SUB_TITLE_1 = 'Sub-Title-1'


class FontsNames(Enum):
    OPENSANS_REGULAR = "OpenSans-Regular"
    OPENSANS_BOLD = "OpenSans-Bold"
    CONTHRAX = "Conthrax"
    ARIALNARROW = "Arial-Narrow"
    ARIALNARROW_BOLD = "Arial-Narrow-Bold"
    ARIALNARROW_ITALIC = "Arial-Narrow-Italic"
    ARIALNARROW_BOLD_ITALIC = "Arial-Narrow-Bold-Italic"


class CustomTableStyles(Enum):
    DEFAULT = 'default'

class CustomTableStyle:
    def __init__(self, table_style, cell_styles=None) -> None:
        self.table_style = table_style
        self.cell_styles = cell_styles or self._default_cell_styles()
        self.left_margin = self.right_margin = 0
        self.top_margin = self.bottom_margin = 0

        self.set_margin()

    def set_margin(self, left_margin: int = 2.5 * cm, right_margin: int = 2.5 * cm, top_margin: int =  2 * cm, bottom_margin: int = 2 * cm):
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin

    def _default_cell_styles(self):
        styles = [
            {'fontName': FontsNames.ARIALNARROW.value, 'fontSize': 10, 'textColor': HexColor(0x000000)},       # Content style
        ]
        return styles

    def get_cell_styles(self, row: int):
        return self.cell_styles[row % len(self.cell_styles)]

    def get_paragraph_style(self, row: int, col: int) -> ParagraphStyle:
        style_dict = self.get_cell_styles(row)
        return ParagraphStyle(name=f'Custom-{row}-{col}',
                              fontName=style_dict['fontName'],
                              fontSize=style_dict['fontSize'],
                              textColor=style_dict['textColor'],
                              alignment=TA_CENTER)

class Theme:
    def __init__(self) -> None:
        self.style_sheet = getSampleStyleSheet()
        self.colors = self._define_colors()
        self.leftMargin = self.rightMargin = 2.5 * cm
        self.topMargin = self.bottomMargin = 2 * cm
        self.page_width, self.page_height = LETTER
        self._register_fonts()
        self._initialize_paragraph_styles()
        self._initialize_table_styles()

    def _define_colors(self):
        return {
            'orange': HexColor(0xF96611),
            'yellow': HexColor(0xF9A40E),
            'blue': HexColor(0x4AAEC9),
            'table_blue': HexColor(0xC5E1FF),
            'dark_blue': HexColor(0x195C74),
            'light_blue': HexColor(0x3796BF),
            'gray': HexColor(0x8C8984),
            'black': HexColor(0x000000),
            'white': HexColor(0xFFFFFF),
            'whitesmoke': HexColor(0xF5F5F5),
            'lightgrey': HexColor(0xD3D3D3)
        }

    def _register_fonts(self):
        try:
            for name, path in FONTS:
                pdfmetrics.registerFont(TTFont(name, path))

            os.makedirs(CHARTS_DIR, exist_ok=True)
            shutil.rmtree(CHARTS_DIR)
            os.makedirs(CHARTS_DIR, exist_ok=True)
        except Exception as e:
            print(f"Error loading fonts or creating folders: {e}")
            exit(1)

    def _initialize_paragraph_styles(self):
        styles = self.style_sheet

        styles.add(ParagraphStyle(ParagraphStyles.TEXT_NORMAL.value,
                                  fontName="Arial-Narrow",
                                  fontSize=12,
                                  spaceAfter=12,
                                  alignment=TA_JUSTIFY,
                                  leading=13.8))

        styles.add(ParagraphStyle(ParagraphStyles.SUB_TEXT_NORMAL.value,
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value],
                                  leftIndent=1 * cm))

        styles.add(ParagraphStyle(ParagraphStyles.TEXT_BOLD.value,
                                  fontName="Arial-Narrow-Bold",
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value]))

        styles.add(ParagraphStyle(ParagraphStyles.TABLE_HEADER.value,
                                  fontName="Arial-Narrow-Bold",
                                  fontSize=12,
                                  alignment=TA_CENTER,
                                  textColor=self.colors['white'],
                                  leading=13.8))

        styles.add(ParagraphStyle(ParagraphStyles.TABLE_HEADER_CONTENT.value,
                                  alignment=TA_CENTER,
                                  spaceAfter=0,
                                  leftIndent=0,
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value]))

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
        
        styles.add(ParagraphStyle(name=ParagraphStyles.SUB_TITLE_1.value,
                                  fontName='Arial-Narrow-Bold',
                                  fontSize=12,
                                  textColor=self.colors['black'],
                                  spaceBefore=6,
                                  spaceAfter=6,
                                  leftIndent=0,
                                  # firstLineIndent=17.9,
                                  alignment=TA_LEFT,
                                  leading=20.7,
                                  firstLineIndent=28.9))

        styles.add(ParagraphStyle(name=ParagraphStyles.LIST.value,
                                  parent=styles[ParagraphStyles.TEXT_NORMAL.value],
                                  spaceAfter=6,
                                  spaceBefore=6,
                                  leading=13.8))

        styles.add(ParagraphStyle(name=ParagraphStyles.SUB_LIST.value,
                                  parent=styles[ParagraphStyles.LIST.value],
                                  leftIndent=1 * cm))

    def _initialize_table_styles(self):
        self.table_styles = {
            CustomTableStyles.DEFAULT.value: CustomTableStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor("#8cbbd2")),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.get("white")),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), FontsNames.ARIALNARROW_BOLD.value),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors.get("whitesmoke")),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors.get("black")),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), FontsNames.ARIALNARROW.value),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), HexColor("#333333")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors.get("whitesmoke"), self.colors.get("lightgrey")]),
                ('WORDWRAP', (0, 0), (-1, -1), True)
            ]))
        }

    def get_style(self, style_name: ParagraphStyles | CustomTableStyles | str) -> ParagraphStyle | CustomTableStyle:
        if isinstance(style_name, str):
            if style_name in self.style_sheet:
                return self.style_sheet.get(style_name)
            return self.table_styles.get(style_name, self.table_styles[CustomTableStyles.DEFAULT.value])
        elif isinstance(style_name, CustomTableStyles):
            return self.table_styles.get(style_name.value)
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

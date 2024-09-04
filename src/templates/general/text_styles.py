from enum import Enum

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.units import cm

class FontSize(Enum):
    SMALL = 8
    MEDIUM = 10
    LARGE = 12
    XLARGE = 14
    X2LARGE = 16
    X3LARGE = 18
    X4LARGE = 22
    X4_5LARGE = 24
    X5LARGE = 26

class FontFamily(Enum):
    OPEN_SANS = "OpenSans"
    CONTHRAX = "Conthrax"
    ARIAL_NARROW = "Arial-Narrow"

class FontStyle(Enum):
    REGULAR = "Regular"
    BOLD = "Bold"
    ITALIC = "Italic"
    BOLD_ITALIC = "Bold-Italic"

class CustomParagraphStyle(Enum):
    TITLE_COVER_TEXT = "TitleCoverText"
    TITLE_1 = "Title1"
    TITLE_2 = "Title2"
    NORMAL_TEXT = "NormalText"

class CustomColor(Enum):
    PRIMARY = Color(33/255, 88/255, 104/255, 1)  # RGB(33, 88, 104)

# Estilo: TitleCoverText
# Fuente: 26 pto, Negrita, Color de fuente: Color personalizado(RGB(33;88;104)), Centrado
#     Interlineado:  sencillo, Espacio
#     Antes:  12 pto, No agregar espacio entre párrafos del mismo estilo
#     Basado en: Normal
TitleCoverText = ParagraphStyle(
    CustomParagraphStyle.TITLE_COVER_TEXT.value,
    parent=None,
    fontName=FontFamily.ARIAL_NARROW.value + "-" + FontStyle.BOLD.value,
    fontSize=FontSize.X5LARGE.value,
    textColor=CustomColor.PRIMARY.value,
    alignment=TA_CENTER,
    spaceBefore=12,
    spaceAfter=0,
    leading=12,
    wordWrap=True
)

# Estilo: Title1
# Fuente: (Asiática) Times New Roman, 18 pto, Negrita, Color de fuente: Color personalizado(RGB(68;84;106)), Español (Venezuela), Sangría:
#     Izquierda:  0 cm
#     Sangría francesa:  0,63 cm, Justificado, Espacio
#     Antes:  30 pto
#     Después:  24 pto, Conservar con el siguiente, Conservar líneas juntas, Nivel 1, Esquema numerado + Nivel: 1 + Estilo de numeración: 1, 2, 3, … + Iniciar en: 1 + Alineación: Izquierda + Alineación:  0 cm + Sangría:  0,63 cm
#     Basado en: Normal
Title1 = ParagraphStyle(
    CustomParagraphStyle.TITLE_1.value,
    parent=None,
    fontName=FontFamily.ARIAL_NARROW.value + "-" + FontStyle.BOLD.value,
    fontSize=FontSize.X4_5LARGE.value,
    textColor=HexColor("#44546A"),
    alignment=TA_JUSTIFY,
    spaceBefore=30,
    spaceAfter=24,
    leading=24,
    wordWrap=True
)

TEXT_STYLES = {
    CustomParagraphStyle.TITLE_COVER_TEXT.value: TitleCoverText,
    CustomParagraphStyle.TITLE_1.value: Title1
}

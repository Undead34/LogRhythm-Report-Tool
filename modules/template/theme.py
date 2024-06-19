from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from enum import Enum
from reportlab.lib.units import cm


class ParagraphStyles(Enum):
    NR_TEXTO_1 = 'NR-Texto 1'
    NR_TEXTO_1_BLOB = 'NR-Texto-Blob 1'
    NR_TEXTO_NGRAFICO = 'NR-Texto NGrafico'
    NR_TITULO_1 = 'NR-Titulo 1'
    NR_TITULO_2 = 'NR-Titulo 2'
    NR_TITULO_3 = 'NR-Titulo 3'
    NR_TABLE_HEADER_1 = 'NR-Table Header 3'
    NR_TABLE_HEADER_CONTENT_1 = 'NR-Table Header Content 3'
    NR_TEXTO_ITALIC = 'NR-Italic'


class Theme():
    def __init__(self) -> None:
        self.styleSheet = getSampleStyleSheet()

        self.NetReadyOrange = HexColor(0xF96611)
        self.NetReadyYellow = HexColor(0xF9A40E)
        self.NetReadyBlue = HexColor(0x4AAEC9)
        self.NetReadyTableBlue = HexColor(0xC5E1FF)
        self.NetReadyDarkBlue = HexColor(0x195C74)
        self.NetReadyLightBlue = HexColor(0x3796BF)
        self.NetReadyGray = HexColor(0x8C8984)

        self.Black = HexColor(0x000000)
        self.White = HexColor(0xFFFFFF)

        self._set_paragraph_styles()

    def _set_paragraph_styles(self):
        styles = self.styleSheet

        # Fuente: Arial Narrow, 12 pto, Sangría:
        # Izquierda:  1 cm, Justificado
        # Interlineado:  Múltiple 1,15 lín., Espacio
        # Después:  12 pto, Estilo: Mostrar en la galería de estilos
        styles.add(ParagraphStyle(ParagraphStyles.NR_TEXTO_1.value,
                                  fontName="Arial-Narrow",
                                  fontSize=12,
                                  spaceAfter=12,
                                  #   leftIndent=28.34,
                                  alignment=TA_JUSTIFY,
                                  leading=13.8
                                  ))

        # Fuente: Arial Narrow, 12 pto, Sangría:
        # Izquierda:  1 cm, Justificado
        # Interlineado:  Múltiple 1,15 lín., Espacio
        # Después:  12 pto, Estilo: Mostrar en la galería de estilos
        styles.add(ParagraphStyle(ParagraphStyles.NR_TEXTO_1_BLOB.value,
                                  fontName="Arial-Narrow-Bold",
                                  parent=styles[ParagraphStyles.NR_TEXTO_1.value],
                                  ))

        # Fuente: Arial Narrow, 12 pto, Sangría:
        # Izquierda:  1 cm, Justificado
        # Interlineado:  Múltiple 1,15 lín., Espacio
        # Después:  12 pto, Estilo: Mostrar en la galería de estilos
        styles.add(ParagraphStyle(ParagraphStyles.NR_TABLE_HEADER_1.value,
                                  fontName="Arial-Narrow-Bold",
                                  fontSize=12,
                                  alignment=TA_CENTER,
                                  textColor=self.White,
                                  leading=13.8
                                  ))

        # Fuente: Arial Narrow, 12 pto, Sangría:
        # Izquierda:  1 cm, Justificado
        # Interlineado:  Múltiple 1,15 lín., Espacio
        # Después:  12 pto, Estilo: Mostrar en la galería de estilos
        styles.add(ParagraphStyle(ParagraphStyles.NR_TABLE_HEADER_CONTENT_1.value,
                                  alignment=TA_CENTER,
                                  spaceAfter=0,
                                  leftIndent=0,
                                  parent=styles[ParagraphStyles.NR_TEXTO_1.value],
                                  ))

        # Definimos el estilo 'NR-Texto NGrafico'
        styles.add(ParagraphStyle(name=ParagraphStyles.NR_TEXTO_NGRAFICO.value,
                                  fontName='Arial-Narrow-Bold-Italic',
                                  fontSize=11,
                                  textColor=self.Black,
                                  spaceBefore=6,  # Espacio antes: 6 pto
                                  spaceAfter=14,  # Espacio después: 20 pto
                                  # Sangría primera línea: 1cm (en puntos)
                                  firstLineIndent=1 * cm,
                                  alignment=TA_CENTER))  # Centrado
        
        # Definimos el estilo 'NR-Texto NGrafico'
        styles.add(ParagraphStyle(name=ParagraphStyles.NR_TEXTO_ITALIC.value,
                                  fontName='Arial-Narrow-Italic',
                                  fontSize=11,
                                  textColor=self.Black,
                                  alignment=TA_CENTER))  # Centrado

        # Definimos el estilo 'NR-Titulo 1'
        styles.add(ParagraphStyle(name=ParagraphStyles.NR_TITULO_1.value,
                                  fontName='Arial-Narrow-Bold',
                                  fontSize=18,
                                           textColor=self.NetReadyLightBlue,
                                           spaceBefore=30,  # Espacio antes: 30 pto
                                           spaceAfter=24,  # Espacio después: 24 pto
                                           leftIndent=0,  # Sangría izquierda: 0 cm
                                           # Sangría francesa: 0,63 cm (en puntos)
                                           firstLineIndent=17.9,
                                           alignment=TA_CENTER,  # Justificado
                                           leading=20.7))  # Interlineado: Múltiple 1,15 lín.

        # Definimos el estilo 'NR-Titulo 2' basado en 'NR-Titulo 1'
        styles.add(ParagraphStyle(name=ParagraphStyles.NR_TITULO_2.value,
                                  # Basado en: NR-Titulo 1
                                  parent=styles[ParagraphStyles.NR_TITULO_1.value],
                                  alignment=TA_JUSTIFY,))

        # Definimos el estilo 'NR-Titulo 3' basado en 'NR-Titulo 1'
        styles.add(ParagraphStyle(name=ParagraphStyles.NR_TITULO_3.value,
                                  # Basado en: NR-Titulo 1
                                  parent=styles[ParagraphStyles.NR_TITULO_1.value],
                                  leftIndent=0,  # Sangría izquierda: 0 cm
                                  firstLineIndent=28.9))  # Sangría francesa: 1,02 cm (en puntos)

    def get_style(self, style_name: ParagraphStyles | str) -> ParagraphStyles:
        if type(style_name) == str:
            return self.styleSheet.get(style_name)
        else:
            return self.styleSheet.get(style_name.value)

    def replace_bold_with_font(self, text):
        import re
        return re.sub(r'\*\*(.*?)\*\*', r'<font face="Arial-Narrow-Bold">\1</font>', text)
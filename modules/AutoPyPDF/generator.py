# ReportLab Libraries
from reportlab.platypus import PageBreak, Image, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

# Libraries
from datetime import datetime
from matplotlib.patches import Wedge
from AutoPyPDF.canvas import Canvas
from AutoPyPDF.report import Report
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shutil
import math
import uuid
import os


try:
    # Ruta al archivo .ttf de Arial Narrow en Windows
    pdfmetrics.registerFont(
        TTFont("Arial-Narrow", "assets/fonts/Arial Narrow.ttf"))
    pdfmetrics.registerFont(TTFont("Conthrax", "assets/fonts/Conthrax.ttf"))
    pdfmetrics.registerFont(
        TTFont("OpenSans-Regular", "assets/fonts/OpenSans-Regular.ttf"))
    pdfmetrics.registerFont(
        TTFont("OpenSans-Bold", "assets/fonts/OpenSans-Bold.ttf"))

    os.makedirs("out/charts", exist_ok=True)
    shutil.rmtree("out/charts")
    os.makedirs("out/charts", exist_ok=True)
except:
    print(
        "An error occurred when starting the application.\n"
        "details: The error occurred when trying to load the fonts and/or create the necessary folders.")
    exit(1)


class GenerateReport():
    def __init__(self, output: str, metadata: dict) -> None:
        self.output = output
        Canvas.metadata = metadata
        self.elements = []
        self.width, self.height = LETTER
        self.styleSheet = getSampleStyleSheet()
        self.doc = Report(output, pagesize=LETTER)
        self.inch = inch

        self.constants = {
            "inch": inch,
            "colors": "red",
        }

        self.NetReadyOrange = HexColor(0xF96611)
        self.NetReadyYellow = HexColor(0xF9A40E)
        self.NetReadyBlue = HexColor(0x4AAEC9)
        self.NetReadyTableBlue = HexColor(0xC5E1FF)
        self.NetReadyDarkBlue = HexColor(0x195C74)
        self.NetReadyLightBlue = HexColor(0x3796BF)
        self.NetReadyGray = HexColor(0x8C8984)
        self.NetReadyBlack = HexColor(0x000000)
        self.NetReadyWhite = HexColor(0xFFFFFF)

    def build(self):
        self.doc.multiBuild(self.elements, canvasmaker=Canvas)

    def pageHeader(self, header: str):
        HeaderStylePrimary = ParagraphStyle("HeaderPrimary",
                                            fontName="Conthrax",
                                            fontSize=16,
                                            alignment=TA_LEFT,
                                            borderWidth=3,
                                            textColor=self.NetReadyDarkBlue,
                                            spaceAfter=10)

        self.elements.append(Paragraph(header, HeaderStylePrimary))

        d = Drawing(self.width - inch * 2, 1)
        line = Line(0, 0, self.width - inch * 2, 0)
        line.strokeColor = self.NetReadyGray
        line.strokeWidth = 1
        d.add(line)
        self.elements.append(d)

    # Public

    def firstPage(self, title: str, footer: str, leftImage="assets/images/logrhythm.png"):
        # The image in the upper right corner and inside the margin
        img = Image(leftImage, kind="proportional")
        img.drawHeight = 0.5 * inch
        img.drawWidth = 2.4 * inch
        img.hAlign = "LEFT"
        self.elements.append(img)

        titleStyle = ParagraphStyle("DocumentTitle",
                                    fontName="Conthrax",
                                    fontSize=22,
                                    leading=24,
                                    alignment=TA_CENTER,
                                    spaceBefore=220,
                                    spaceAfter=240
                                    )

        self.elements.append(Paragraph(title, titleStyle))

        summaryStyle = ParagraphStyle("Summary", fontName="Arial-Narrow", fontSize=10,
                                      leading=14, justifyBreaks=1, alignment=TA_LEFT, justifyLastLine=1)

        self.elements.append(Paragraph(footer, summaryStyle))
        self.elements.append(PageBreak())

    def addParagraph(self, text, font="Arial-Narrow", fontSize=12, spaceBefore=10, spaceAfter=10, textColor=None):
        if not textColor:
            textColor = self.NetReadyBlack

        paragraphStyle = ParagraphStyle("TableTitle",
                                        fontName=font,
                                        fontSize=fontSize,
                                        alignment=TA_LEFT,
                                        borderWidth=3,
                                        textColor=textColor,
                                        spaceBefore=spaceBefore,
                                        spaceAfter=spaceAfter)

        self.elements.append(Paragraph(text, paragraphStyle))

    def addSubTitle(self, sub_title: str, fontSize=14, spaceBefore=10, spaceAfter=10):
        subTitleStyle = ParagraphStyle("TableTitle",
                                       fontName="Conthrax",
                                       fontSize=fontSize,
                                       alignment=TA_LEFT,
                                       borderWidth=3,
                                       textColor=self.NetReadyLightBlue,
                                       spaceBefore=spaceBefore,
                                       spaceAfter=spaceAfter)

        self.elements.append(Paragraph(sub_title, subTitleStyle))

    def addPageBreak(self):
        self.elements.append(PageBreak())

    def addPieChart(self, x: list[int], labels: list[str], colors: list[str] = None, chartHeight: float | int = inch * 2, chartWidth: float | int = inch * 3.2, hAlign: str = "CENTER"):
        fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
        pieChart = ax.pie(x, wedgeprops=dict(width=0.5),
                          startangle=0, colors=colors)
        ax.legend(pieChart[0], labels, title="Data",
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        tmpPath = f"out/charts/{uuid.uuid4()}.png"
        fig.savefig(tmpPath, transparent=True,
                    bbox_inches='tight', pad_inches=0.1)
        self.addImage(tmpPath, chartWidth, chartHeight, hAlign)
        plt.close()

    def addTable(self, title, column_headers, data_rows, column_styles, title_style=None, col_widths=None):
        self.elements.append(Spacer(0, 22))

        if title_style is None:
            title_style = ParagraphStyle("TableTitle",
                                         fontName="Conthrax",
                                         fontSize=12,
                                         alignment=TA_LEFT,
                                         borderWidth=3,
                                         textColor=self.NetReadyLightBlue)

        self.elements.append(Paragraph(title, title_style))
        self.elements.append(Spacer(0, 22))

        # Header data
        header_data = []
        centered = ParagraphStyle(name="centered", alignment=TA_LEFT)

        for header in column_headers:
            ptext = "<font size='10'><b>%s</b></font>" % header
            header_paragraph = Paragraph(ptext, centered)
            header_data.append(header_paragraph)

        table_data = [header_data, [Spacer(0, 2)
                                    for _ in range(len(column_headers))]]
        table_bg = []

        # Content data
        for row_data in data_rows:
            formatted_row = []
            for idx, item in enumerate(row_data):
                ptext = "<font size='8'>%s</font>" % item
                p = Paragraph(ptext, column_styles[idx])
                formatted_row.append(p)
            table_data.append(formatted_row)

        for idx, item in enumerate(table_data):
            if idx == 0:
                table_bg.append(
                    ("BACKGROUND", (0, idx), (-1, idx), self.NetReadyWhite))
                continue

            if (idx+1) % 2 != 0:
                table_bg.append(
                    ("BACKGROUND", (0, idx), (-1, idx), self.NetReadyTableBlue))
            else:
                table_bg.append(
                    ("BACKGROUND", (0, idx), (-1, idx), self.NetReadyWhite))

        # Create table
        table = Table(table_data, colWidths=col_widths if col_widths else [
                      (self.width - inch * 2) / len(column_headers) for _ in range(len(column_headers))])
        tStyleArray = [
            # ("ALIGN", (0, 0), (0, -1), "CENTER"),  # Primera columna LEFT
            # ("ALIGN", (1, 0), (1, -1), "CENTER"),  # Segunda columna CENTER
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),  # Las demás columnas LEFT
            ('LINEABOVE', (0, 1), (-1, 1), 0.5, self.NetReadyGray),
        ]

        tStyle = TableStyle(tStyleArray + table_bg)
        table.setStyle(tStyle)
        self.elements.append(table)

    def addImage(self, image: str, width: int | float, height: int | float, hAlign="LEFT", kind="proportional", mask="auto"):
        img = Image(image, kind=kind, mask=mask)
        img.drawWidth = width
        img.drawHeight = height
        img.hAlign = hAlign
        self.elements.append(img)

    def standard_deviation(self, values):
        promedio = sum(values) / len(values)
        suma = sum([(x - promedio) ** 2 for x in values])
        return math.sqrt(suma / len(values))

    def coefficient_variation(self, values):
        promedio = sum(values) / len(values)
        desv_std = self.standard_deviation(values)
        return (desv_std / promedio) * 100

    def addBarHChart(self, x: list[int], labels: list[str], xlabel: str, colors: list[str] = None, chartHeight: float | int = inch * 2, chartWidth: float | int = inch * 3.2, hAlign: str = "CENTER", showNum=False):
        plt.close()
        if not colors:
            colors = plt.get_cmap("Blues")(np.linspace(0.4, 1, len(labels)))

        # Creación del gráfico
        fig, ax = plt.subplots(figsize=(10, 4.5))
        bars = ax.barh(labels, x, color=colors)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel)
        # ax.set_title(title)

        # Añadir valores en cada barra
        for bar in bars:
            width = bar.get_width()

            if (self.coefficient_variation(x) >= 80 or showNum):
                posX = width - \
                    len(str(width)) if len(str(width)) != 1 else width + 5

                ax.text(posX,
                        bar.get_y() + bar.get_height() / 2,
                        int(width),
                        ha="right",
                        va="center",
                        color="black")

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)

        # Mostrar el gráfico
        plt.tight_layout()
        tmpPath = f"out/charts/{uuid.uuid4()}.png"
        fig.savefig(tmpPath, transparent=True,
                    bbox_inches="tight", pad_inches=0.1, dpi=250)
        self.addImage(tmpPath, chartWidth, chartHeight, hAlign)
        plt.close()

    def addSubTitle2(self, subTitle: str, alignment=TA_LEFT, fontSize=12):
        self.elements.append(Spacer(0, 22))

        title_style = ParagraphStyle("SubTitle2",
                                     fontName="Conthrax",
                                     fontSize=fontSize,
                                     alignment=alignment,
                                     borderWidth=3,
                                     textColor=self.NetReadyLightBlue)

        self.elements.append(Paragraph(subTitle, title_style))
        self.elements.append(Spacer(0, 22))

    def addGauge(self, value, max_value, min_value=0, title="", colors=["#007DC3", "#FFFFFF"], chartHeight: float | int = inch * 2, chartWidth: float | int = inch * 3.2, hAlign: str = "CENTER"):
        fig, ax = plt.subplots()

        # Define el rango de ángulos basado en el valor y el valor máximo
        angle_range = 180 * (value / max_value)

        # Dibuja la parte llena en la izquierda
        value_wedge = Wedge((0., 0.), .4, 180-angle_range,
                            180, facecolor=colors[0], width=0.10)
        ax.add_patch(value_wedge)

        # Dibuja el fondo (parte no llena) a la derecha del valor lleno
        bg_wedge = Wedge((0., 0.), .4, 0, 180-angle_range,
                         facecolor=colors[1], width=0.10)
        ax.add_patch(bg_wedge)

        # Configura el título y estética del gráfico
        ax.text(0, 0.18, str(value), ha="center", va="center",
                fontsize=42, fontweight="bold", color="#80D0FF")
        ax.text(0, 0.05, title, ha="center", va="baseline",
                fontsize=16, fontweight="bold", color="#CCCCCC")

        # Añade los números en los extremos
        ax.text(-0.35, 0.02, str(min_value), ha="center",
                va="center", fontsize=12, fontweight="bold")
        ax.text(0.35, 0.02, str(max_value), ha="center",
                va="center", fontsize=12, fontweight="bold")

        ax.set_frame_on(False)
        ax.axes.set_xticks([])
        ax.axes.set_yticks([])
        ax.axis('equal')
        plt.tight_layout()
        tmpPath = f"out/charts/{uuid.uuid4()}.png"
        fig.savefig(tmpPath, transparent=True,
                    bbox_inches='tight', pad_inches=0.1, dpi=250)
        plt.close()

        self.addImage(tmpPath, chartWidth, chartHeight, hAlign)

    def addSpace(self, x: int | float, y: int | float):
        self.elements.append(Spacer(x, y))

    def addLineChart(self, x: list[list[int]], dateRange: tuple[str], yLabels: list[int] | list[str], labels: list[str], chartWidth: float | int = inch * 3.2, chartHeight: float | int = inch * 2,  hAlign: str = "CENTER"):
        # Determinar la diferencia entre las fechas
        start_date = datetime.strptime(dateRange[0], "%d/%m/%Y")
        end_date = datetime.strptime(dateRange[1], "%d/%m/%Y")
        difference = (end_date - start_date).days

        # Establecer la frecuencia en base a la diferencia
        freq = "M"
        if difference <= 90:  # aproximadamente 3 meses
            freq = "W"

        # Crear rango de fechas usando pandas
        datesRange = pd.date_range(
            start=dateRange[0], end=dateRange[1], freq=freq)

        # Crear la gráfica
        fig, ax = plt.subplots()

        # Configuraciones para el eje Y
        ax.set_yscale("symlog")
        ax.set_yticks(yLabels)
        for y in yLabels:
            ax.axhline(y=y, color="black", linewidth=0.5,
                       alpha=1, antialiased=False)

        # Configurar el eje X
        ax.set_xticks(datesRange)

        if freq == "M":
            ax.xaxis.set_major_formatter(
                plt.FixedFormatter(datesRange.strftime("%b")))
        elif freq == "W":
            ax.xaxis.set_major_formatter(
                plt.FixedFormatter(datesRange.strftime("%d-%b")))

        def y_format(x, pos):
            if x >= 1000:
                return f"{int(x/1000)}k"
            else:
                return f"{int(x)}"
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(y_format))

        # Eliminar bordes innecesarios y rotar las etiquetas del eje X
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        plt.xticks(rotation=45)

        # Añadir series de datos
        for idx, valores in enumerate(x):
            # Si las longitudes no coinciden, ajusta la serie de datos
            if len(datesRange) != len(valores):
                valores = valores[:len(datesRange)]
            ax.plot(datesRange, valores, linewidth=2, label=labels[idx])
            ax.text(datesRange[len(valores)-1], valores[-1],
                    labels[idx], verticalalignment='bottom')

        # Mostrar leyenda
        ax.legend()

        # Mostrar la gráfica
        plt.tight_layout()
        tmpPath = f"out/charts/{uuid.uuid4()}.png"
        fig.savefig(tmpPath, transparent=True,
                    bbox_inches='tight', pad_inches=0.1, dpi=250)
        plt.close()

        self.addImage(tmpPath, chartWidth, chartHeight, hAlign)

    def addSquares(self, values: list[str], labels: list[str], chartWidth: float | int = inch * 3.2, chartHeight: float | int = inch * 2,  hAlign: str = "CENTER"):
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing, String, Rect
        from reportlab.pdfbase.pdfmetrics import stringWidth

        def calculate_block_size(value, label, font_size_value=30, font_size_label=10.5):
            textSize_value = stringWidth(
                value, "OpenSans-Bold", font_size_value)
            textSize_label = stringWidth(
                label, "OpenSans-Bold", font_size_label)
            return max(textSize_value, textSize_label)

        def add_text_to_drawing(drawing, position, value, label, block_size, font_size_value=30, font_size_label=10.5):
            textSize_value = stringWidth(
                value, "OpenSans-Bold", font_size_value)
            textSize_label = stringWidth(
                label, "OpenSans-Bold", font_size_label)

            xPos_value = position + (block_size - textSize_value) / 2
            xPos_label = position + (block_size - textSize_label) / 2

            drawing.add(String(xPos_value, 50, value, fontSize=font_size_value,
                        fillColor=HexColor("#3796bf"), fontName="OpenSans-Bold"))
            drawing.add(String(xPos_label, 30, label, fontSize=font_size_label,
                        fillColor=HexColor("#000000"), fontName="OpenSans-Bold"))
            return drawing

        # Ancho de la pantalla menos los dos margenes laterales
        width = self.width - (2 * self.inch)
        mx = width / 20

        block_0 = mx*2 + calculate_block_size(values[0], labels[0])
        block_1 = mx*2 + calculate_block_size(values[1], labels[1])

        # Calcular la posición del eje X para centrar el rectángulo
        xPos = (width - (block_0 + block_1)) / 2

        d = Drawing(width, 100)
        d.add(Rect(xPos, 0, block_0+block_1, 100, fillColor=HexColor("#e9f0f6")))

        d = add_text_to_drawing(
            d, block_0 -mx*2, values[0], labels[0], block_0)
        d = add_text_to_drawing(d, ((block_0)+(block_1-mx*2))
                                , values[1], labels[1], block_1)

        self.elements.append(d)
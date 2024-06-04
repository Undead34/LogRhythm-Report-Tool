from reportlab.platypus import PageBreak, Image, Spacer, Table, TableStyle, Paragraph
from reportlab.platypus import Table, TableStyle, Indenter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib import colors

from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch, cm

from datetime import datetime
import pandas as pd

from modules.template.theme import ParagraphStyles
from .charts import Charts

from typing import TYPE_CHECKING

from utils import ElementList

if TYPE_CHECKING:
    from modules.report import Report


class Components:
    def __init__(self, report: 'Report') -> None:
        self.report = report
        self.theme = report.theme
        self.db = report.database
        self.pkg = report.packages
        self.charts = Charts(self)

        # Atributo privado _available_tables
        self._available_tables = pd.DataFrame([
            {
                "ID": "entities_table",
                "Name": "Tabla de entidades disponibles en LogRhythm",
                "Callback": self._entities_table
            },
            {
                "ID": "alarms_per_entity_table",
                "Name": "Tabla de alarmas por entidad",
                "Callback": self._alarms_per_entity_table
            }
        ])

        # Atributo privado _available_charts
        self._available_charts = pd.DataFrame([
            {
                "ID": "entities_chart",
                "Name": "Gráfico de entidades disponibles en LogRhythm",
                "Callback": self.charts.histogram_entities_chart
            },
            {
                "ID": "alarms_per_entity_chart",
                "Name": "Gráfico de alarmas por entidad",
                "Callback": self.charts.stacked_bar_entities_chart
            },
        ])

    def cover_page(self, signature: dict, name: str, logo: str):
        t = self.theme
        e = ElementList()

        e += Image("./assets/images/netready.png",
                   width=3.67 * cm,
                   height=3.12 * cm,
                   hAlign="CENTER")

        e += Spacer(0, 4.5 * cm)
        e += Paragraph(signature["title"],
                       t.get_style(ParagraphStyles.NR_TITULO_1))
        e += Spacer(0, 4 * cm)

        e += Image(logo,
                   width=10.37 * cm,
                   height=2.46 * cm,
                   hAlign="CENTER")

        e += Spacer(0, 3 * cm)

        today = datetime.now()
        e += Paragraph(f"""
        <font face=\"Arial-Narrow-Bold\">Nombre del Cliente:</font> {signature['client_name']}<br/>
        <font face=\"Arial-Narrow-Bold\">Fecha del Informe:</font> {today.strftime('%Y-%m-%dT%H:%M:%SZ')}<br/>
        <font face=\"Arial-Narrow-Bold\">Periodo del Informe:</font> Entre {self.db._start_date} y {self.db._end_date}<br/>
        <font face=\"Arial-Narrow-Bold\">Preparado por:</font> {signature['author']}
        """, self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        e += Spacer(0, 1.5 * cm)

        e += Paragraph(f"© {today.year} Soluciones Netready, C.A. All Rights Reserved.",
                    self.theme.get_style(ParagraphStyles.NR_TEXTO_ITALIC))

        e += PageBreak()

        return e

    def get_tables(self) -> pd.DataFrame:
        return self._available_tables.copy()

    def get_charts(self):
        return self._available_charts.copy()

    # Private Components
    # =========================================================

    def _entities_table(self):
        """No sé, pero se puede llamar a self, aunque no se le pasa a la funcion que lo llama en utils, cosas de Python XD"""
        entities = self.db.get_entities().get(['EntityID', 'Name'])

        table_data = [entities.columns.to_list()] + entities.values.tolist()

        return self._table_maker(table_data)

    def _alarms_per_entity_table(self):
        df = self.db.get_alarm_details_by_entity()
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate'])

        # Excluir las alarmas con estado "New" y "OpenAlarm"
        df_filtered = df[~df['AlarmStatus'].isin(['New', 'OpenAlarm'])]

        # Agrupar los datos por 'AlarmName' y 'AlarmStatus'
        alarms = df_filtered.groupby(['Entity', 'AlarmName', 'AlarmStatus']).size(
        ).unstack(fill_value=0).reset_index()

        table_data = [alarms.columns.to_list()] + alarms.values.tolist()

        return self._table_maker(table_data)

    def _table_maker(self, data: list[list]):
        # Verificar que hay más que solo los encabezados
        if not data or len(data) == 1:
            return []

        rows, cols = len(data), len(data[0])
        left_margin, right_margin, sangria = self.report.leftMargin, self.report.rightMargin, 0 * cm
        usable_width = LETTER[0] - left_margin - right_margin - sangria

        header_style = self.theme.get_style(ParagraphStyles.NR_TABLE_HEADER_1)
        body_style = self.theme.get_style(
            ParagraphStyles.NR_TABLE_HEADER_CONTENT_1)

        padding = 12  # Padding adicional

        # Calculamos los anchos iniciales de los encabezados y el contenido
        header_widths = [stringWidth(str(
            data[0][col]), header_style.fontName, header_style.fontSize) + padding for col in range(cols)]
        content_widths = [max(stringWidth(str(data[row][col]), body_style.fontName,
                              body_style.fontSize) + padding for row in range(1, rows)) for col in range(cols)]
        col_widths = [max(h, c) for h, c in zip(header_widths, content_widths)]

        total_width = sum(col_widths)
        min_header_widths = [stringWidth(str(
            data[0][col]), header_style.fontName, header_style.fontSize) + padding for col in range(cols)]

        if total_width > usable_width:
            # Ajustamos las columnas proporcionalmente
            scale_factor = usable_width / total_width
            col_widths = [w * scale_factor for w in col_widths]

            # Verificamos y ajustamos los anchos mínimos de los encabezados
            for i in range(cols):
                if col_widths[i] < min_header_widths[i]:
                    col_widths[i] = min_header_widths[i]

            # Recalculamos el ancho total después del ajuste
            total_width = sum(col_widths)
            if total_width > usable_width:
                # Si aún se excede el ancho utilizable, volvemos a escalar proporcionalmente
                remaining_width = usable_width - sum(min_header_widths)
                remaining_col_widths = [w - min_header_widths[i]
                                        for i, w in enumerate(col_widths)]
                remaining_total_width = sum(remaining_col_widths)

                if remaining_total_width > 0:
                    scale_factor = remaining_width / remaining_total_width
                    for i in range(cols):
                        col_widths[i] = min_header_widths[i] + \
                            (col_widths[i] -
                             min_header_widths[i]) * scale_factor
                else:
                    col_widths = min_header_widths

        # Repartir el espacio restante manteniendo el aspecto ESPEREMOS QUE NO AFECTE EN NADA
        remaining_space = usable_width - total_width
        if remaining_space > 0:
            additional_width = remaining_space / cols
            col_widths = [w + additional_width for w in col_widths]

        table_data = [[Paragraph(str(cell), header_style if i == 0 else body_style)
                       for cell in row] for i, row in enumerate(data)]

        table = Table(table_data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#8cbbd2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Arial-Narrow-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Arial-Narrow'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#333333")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.whitesmoke, colors.lightgrey]),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ])
        table.setStyle(style)

        return [Indenter(left=sangria), table]

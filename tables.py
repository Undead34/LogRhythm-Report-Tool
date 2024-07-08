from reportlab.platypus import Table, TableStyle, Paragraph, Indenter, Spacer
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib import colors

import pandas as pd
from datetime import timedelta

from src.themes.theme import ParagraphStyles
from utils import ElementList

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.components import Components


class Tables():
    def __init__(self, components: 'Components') -> None:
        self.components = components
        self.theme = components.theme
        self.db = components.db
        self.pkg = components.pkg
        self.report = components.report

    def table_of_log_source_type(self):
        """
        Busca un paquete con el _id específico dentro de la lista de paquetes y realiza una acción.
        """
        target_id = "40d28fac-063b-4540-8b5a-bf663f232427"
        
        # Usar una expresión generadora para encontrar el paquete
        package = next((p for p in self.pkg if p._id == target_id), None)
        
        if package:
            data = package.run()
            
            # Verificar si el DataFrame está vacío
            if not data.empty:
                table_data = [data.columns.to_list()] + data.values.tolist()
                table_data[0] = ["Log Source Type", "Count"]
                return self._table_maker(table_data)
            else:
                return [Paragraph("No hay datos disponibles para mostrar la tabla.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]
        else:
            return [Paragraph("No hay datos disponibles para mostrar la tabla.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]


    def table_of_entities(self):
        """No sé, pero se puede llamar a self, aunque no se le pasa a la funcion que lo llama en utils, cosas de Python XD"""
        entities = self.db.get_entities().get(['EntityID', 'Name'])

        table_data = [entities.columns.to_list()] + entities.values.tolist()
        table_data[0] = ["Entity ID", "Entity Name"]

        return self._table_maker(table_data)

    def alarm_status_table(self):
        df = self.db.get_alarms_information()
        df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])

        # Excluir las alarmas con estado "New" y "OpenAlarm"
        df_filtered = df[~df['Alarm Status'].isin(['New', 'Open Alarm'])]

        # Agrupar los datos por 'AlarmName' y 'AlarmStatus'
        alarms = df_filtered.groupby(['Entity Name', 'Alarm Name', 'Alarm Status']).size().unstack(fill_value=0).reset_index()

        table_data = [alarms.columns.to_list()] + alarms.values.tolist()

        elements = ElementList()

        elements += self._table_maker(table_data)

        elements += Paragraph("Tabla de Conteo de Estados de Alarma en LogRhythm", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        elements += Paragraph("""
            Esta tabla proporciona un resumen del número de alarmas en LogRhythm que se han marcado en diferentes estados.
            Excluye las alarmas en estado "Nueva" y "OpenAlarm", enfocándose en aquellos estados que indican un seguimiento o resolución específica.
            La información presentada en esta tabla ayuda a los usuarios a tener una visión clara de la distribución de las alarmas según su estado.
        """, self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def table_ttd_ttr_by_msg_class_name(self):
        """
        Crea una tabla que muestra el tiempo promedio y máximo de detección (TTD) y resolución (TTR)
        de alarmas agrupadas por clase de mensaje.
        """
        df = self.db.get_TTD_AND_TTR_by_msg_class_name()

        # Formatear tiempos en HH:MM:SS
        for col in ['Avg_TTD', 'Max_TTD', 'Avg_TTR', 'Max_TTR']:
            df[col] = df[col].apply(lambda x: str(timedelta(seconds=int(x))) if pd.notnull(x) else '00:00:00')
        
        # Verificar si el DataFrame está vacío
        if not df.empty:
            df.columns = ['Clase de Mensaje', 'Alarmas', 'TTD Promedio', 'TTD Máximo', 'TTR Promedio', 'TTR Máximo']
            table_data = [df.columns.to_list()] + df.values.tolist()
            elements = ElementList()

            # Agregar explicación
            elements += Paragraph(
                "Esta tabla proporciona un resumen del tiempo promedio y máximo de detección (TTD) y resolución (TTR) "
                "de alarmas agrupadas por clase de mensaje. TTD es el tiempo desde que se generó la alarma hasta que se investigó, "
                "y TTR es el tiempo desde que se investigó hasta que se resolvió.",
                self.theme.get_style(ParagraphStyles.NR_TEXTO_1)
            )

            # Crear la tabla
            elements += self._table_maker(table_data, mode='auto', padding=8, sangria=0)

            return elements
        else:
            return [Paragraph("No hay datos disponibles para mostrar la tabla.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

    def table_top_10_alarms(self) -> ElementList:
        df = self.db.get_alarms_information()

        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar la tabla.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        # Contar las ocurrencias de cada alarma
        alarm_counts = df['AlarmName'].value_counts().head(10).reset_index()
        alarm_counts.columns = ['AlarmName', 'Count']

        # Crear los datos de la tabla
        table_data = [alarm_counts.columns.to_list()] + alarm_counts.values.tolist()

        elements = ElementList()
        elements += self._table_maker(table_data)

        elements += Paragraph("Top 10 Alarmas", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        elements += Paragraph("""
            Esta tabla muestra las 10 alarmas más frecuentes en LogRhythm.
            La información presentada en esta tabla ayuda a los usuarios a identificar rápidamente las alarmas más comunes y tomar las medidas necesarias.
        """, self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _table_maker(self, data: list[list], mode: str = 'auto', padding: int = 12, sangria: int = 0,
                    custom_style: dict = None, include_totals: bool = False, totals_columns: list = None,
                    max_width: int = None, min_width: int = None, truncate_text: bool = False, truncate_length: int = 20):
        if not data or len(data) == 1:
            return []

        rows, cols = len(data), len(data[0])
        left_margin, right_margin = self.report.leftMargin, self.report.rightMargin
        usable_width = LETTER[0] - left_margin - right_margin - sangria

        header_style = self.theme.get_style(ParagraphStyles.NR_TABLE_HEADER_1)
        body_style = self.theme.get_style(ParagraphStyles.NR_TABLE_HEADER_CONTENT_1)

        def calculate_column_widths(data, style, padding):
            return [
                max(stringWidth(str(cell), style.fontName, style.fontSize) + padding for cell in column)
                for column in zip(*data)
            ]

        header_widths = calculate_column_widths(data[:1], header_style, padding)
        content_widths = calculate_column_widths(data[1:], body_style, padding)
        col_widths = [max(h, c) for h, c in zip(header_widths, content_widths)]

        total_width = sum(col_widths)

        if max_width:
            col_widths = [min(w, max_width) for w in col_widths]
        if min_width:
            col_widths = [max(w, min_width) for w in col_widths]

        if mode == 'equal':
            col_widths = [usable_width / cols] * cols
        elif mode == 'fit-full':
            col_widths = self._adjust_widths_fit_full(col_widths, total_width, usable_width)
        elif mode == 'auto':
            col_widths = self._adjust_widths_auto_v2(col_widths, total_width, usable_width, header_widths)
        else:  # Default to 'fit'
            if total_width > usable_width:
                scale_factor = usable_width / total_width
                col_widths = [w * scale_factor for w in col_widths]

        if include_totals and totals_columns:
            totals_row = []
            for col in range(cols):
                if col in totals_columns:
                    try:
                        total = sum(float(data[row][col]) for row in range(1, rows))
                        totals_row.append(total)
                    except ValueError:
                        totals_row.append('N/A')
                else:
                    totals_row.append('')
            data.append(totals_row)

        table_data = [
            [
                Paragraph(str(cell)[:truncate_length] + '...' if truncate_text and len(str(cell)) > truncate_length else str(cell), 
                        header_style if i == 0 else body_style) 
                for cell in row
            ] 
            for i, row in enumerate(data)
        ]

        table = Table(table_data, colWidths=col_widths)
        style = custom_style if custom_style else TableStyle([
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ])
        table.setStyle(style)

        return [Indenter(left=sangria), table]

    def _adjust_widths_fit_full(self, col_widths, total_width, usable_width):
        if total_width < usable_width:
            additional_width = usable_width - total_width
            col_widths = [w + (w / total_width) * additional_width for w in col_widths]
        else:
            scale_factor = usable_width / total_width
            col_widths = [w * scale_factor for w in col_widths]
        return col_widths

    def _adjust_widths_auto_v2(self, col_widths, total_width, usable_width, min_header_widths):
        if total_width > usable_width:
            scale_factor = usable_width / total_width
            col_widths = [w * scale_factor for w in col_widths]

        total_width = sum(col_widths)
        if total_width < usable_width:
            additional_width = usable_width - total_width
            col_widths = [w + additional_width / len(col_widths) for w in col_widths]
        
        for i in range(len(col_widths)):
            if col_widths[i] < min_header_widths[i]:
                col_widths[i] = min_header_widths[i]

        total_width = sum(col_widths)
        if total_width > usable_width:
            remaining_width = usable_width - sum(min_header_widths)
            remaining_col_widths = [w - min_header_widths[i] for i, w in enumerate(col_widths)]
            remaining_total_width = sum(remaining_col_widths)
            if remaining_total_width > 0:
                scale_factor = remaining_width / remaining_total_width
                for i in range(len(col_widths)):
                    col_widths[i] = min_header_widths[i] + (col_widths[i] - min_header_widths[i]) * scale_factor
            else:
                col_widths = min_header_widths

        return col_widths

from reportlab.platypus import Table, TableStyle, Paragraph, Indenter, Spacer
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib import colors

import pandas as pd

from modules.template.theme import ParagraphStyles
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
        df = self.db.get_alarm_details_by_entity()
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

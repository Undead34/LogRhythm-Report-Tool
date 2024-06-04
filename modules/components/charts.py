from reportlab.platypus import PageBreak, Image, Spacer, Table, TableStyle, Paragraph
from reportlab.platypus import Table, TableStyle, Indenter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib.units import inch, cm
from reportlab.lib import colors


from uuid import uuid4 as v4
import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import seaborn.objects as so
import seaborn as sns

from modules.template.theme import ParagraphStyles

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.components import Components


class Charts():
    def __init__(self, components: 'Components') -> None:
        self.components = components
        self.theme = components.theme
        self.db = components.db

    def histogram_entities_chart(self):
        df = self.db.get_alarm_details_by_entity()

        # Verificar si el DataFrame está vacío
        if df.empty:
            # Devolver una figura y un párrafo indicando que no hay datos
            a = Paragraph("No hay datos disponibles para mostrar el histograma.",
                          self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))
            return [a]

        df['AlarmDate'] = pd.to_datetime(df['AlarmDate'])

        # Convertimos la fecha a YYYY-MM-DD
        df['AlarmDate'] = df['AlarmDate'].dt.floor('d')

        # Agrupamos por fecha y nombre
        by_date_and_name = df.groupby(['AlarmDate', 'AlarmName'])
        by_date_and_name = by_date_and_name.size().reset_index(name='Counts')

        # Crear un nuevo DataFrame donde los conteos sean menores a 100
        than = 100
        less_than = by_date_and_name[by_date_and_name['Counts'] < than]

        # Agrupar por 'AlarmDate' y sumar los conteos
        others = less_than.groupby('AlarmDate')['Counts'].sum().reset_index()
        others['AlarmName'] = 'Others'

        # Eliminar las filas con conteos menores a than del DataFrame original
        by_date_and_name = by_date_and_name[by_date_and_name['Counts'] >= than]

        # Agregar el nuevo DataFrame al original
        by_date_and_name = pd.concat(
            [by_date_and_name, others], ignore_index=True)

        figure_src = self._draw_chart_histogram(by_date_and_name)

        a = Image(figure_src,
                  width=15.59 * cm,
                  height=8.52 * cm,
                  hAlign="CENTER")

        b = Paragraph("Figure X: Distribución de Alarmas por Tipo y Estado", self.theme.get_style(
            ParagraphStyles.NR_TEXTO_NGRAFICO))

        return [a, b]

    def stacked_bar_entities_chart(self):
        df = self.db.get_alarm_details_by_entity()
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate'])

        # Excluir las alarmas con estado "New" y "OpenAlarm"
        df_filtered = df[~df['AlarmStatus'].isin(['New', 'OpenAlarm'])]

        # Agrupar los datos por 'AlarmName' y 'AlarmStatus'
        alarms = df_filtered.groupby(['AlarmName', 'AlarmStatus']).size().unstack(fill_value=0)

        figure_src = self._draw_chart_stacked_bar(alarms)

        a = Image(figure_src,
                  width=15.59 * cm,
                  height=8.52 * cm,
                  hAlign="CENTER")

        b = Paragraph("Figure X: Distribución de Alarmas por Tipo y Estado", self.theme.get_style(
            ParagraphStyles.NR_TEXTO_NGRAFICO))
        
        return [a, b]


    def _draw_chart_stacked_bar(self, data: pd.DataFrame) -> str:
        # Definir los colores para las barras
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        # Crear la gráfica de barras apiladas
        data.plot(kind='bar', stacked=True, figsize=(
            18, 10), width=0.8, color=colors)

        # Personalizar la gráfica
        plt.title(None)
        plt.xlabel(None)
        plt.ylabel(None)
        plt.yscale('log')  # Establecer escala logarítmica en el eje Y

        plt.xticks(rotation=90, fontsize='small')
        plt.legend(title='Tipo de Alarma', loc='upper left')

        output = os.path.realpath(f"./output/charts/{v4()}.png")

        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)

        plt.savefig(output, format='png', dpi=400,
                    bbox_inches='tight', pad_inches=0.1)

        # plt.show()

        return output

    def _draw_chart_histogram(self, data: pd.DataFrame) -> str:
        # Ajustar el tamaño de la figura
        plt.figure(figsize=(18, 10))

        # Definir la paleta de colores
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        # Graficar los datos
        for i, (name, group) in enumerate(data.groupby('AlarmName')):
            total_events = group['Counts'].sum()
            color = colors[i % len(colors)]
            plt.plot(group['AlarmDate'], group['Counts'],
                     label=f"{name} - Total: ({total_events})", color=color)

            max_count = group['Counts'].max()
            max_date = group['AlarmDate'][group['Counts'].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(
                0, 10), ha='center', color=color)

            # Si la alarma solo ocurrió en un día, dibujar una línea vertical punteada
            if len(group) == 1:
                plt.axvline(x=group['AlarmDate'].iloc[0],
                            color=color, linestyle='dashed')

        # Ajusta los ticks del eje y
        plt.yticks(np.arange(0, data['Counts'].max(), step=300))

        # Ajustar los ticks del eje x
        plt.xticks(pd.date_range(start=data['AlarmDate'].min(
        ), end=data['AlarmDate'].max(), freq='3D'))

        plt.legend()

        output = os.path.realpath(f"./output/charts/{v4()}.png")

        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)

        plt.savefig(output, format='png', dpi=400,
                    bbox_inches='tight', pad_inches=0.1)

        # plt.show()

        return output

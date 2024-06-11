import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from uuid import uuid4 as v4
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import cm
from modules.template.theme import ParagraphStyles
from utils import ElementList
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.components import Components

class Charts():
    def __init__(self, components: 'Components') -> None:
        self.components = components
        self.theme = components.theme
        self.db = components.db

    def trends_in_alarm_activation_graph(self):
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el histograma.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date']).dt.floor('d')
        by_date_and_name = df.groupby(['Alarm Date', 'Alarm Name']).size().reset_index(name='Counts')

        # Crear un nuevo DataFrame donde los conteos sean menores a 100
        than = 100
        less_than = by_date_and_name[by_date_and_name['Counts'] < than]
        others = less_than.groupby('Alarm Date')['Counts'].sum().reset_index()
        others['Alarm Name'] = 'Others'
        by_date_and_name = by_date_and_name[by_date_and_name['Counts'] >= than]
        by_date_and_name = pd.concat([by_date_and_name, others], ignore_index=True)

        figure_src = self._draw_chart_histogram(by_date_and_name['Alarm Date'], by_date_and_name['Alarm Name'], by_date_and_name['Counts'])

        elements = ElementList()
        elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
        elements += Paragraph("Tendencias en la Activación de Alarmas", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        graph_explanation = [
            """
            Este gráfico proporciona una visualización detallada de la evolución temporal de diferentes alarmas, facilitando la identificación de **tendencias** y **picos** en los datos. Cada línea del gráfico representa una alarma distinta, y el color de cada línea corresponde a su nombre en la **leyenda**. El **total de alarmas** también se indica junto al nombre en la leyenda.
            """,
            """
            El eje **x** muestra las fechas, con **marcas cada tres días**. El eje **y** representa el número de alarmas activadas en una **escala lineal**. Los puntos máximos de cada línea están destacados con **anotaciones** que indican el número máximo de alarmas para esa alarma específica. Además, las **alarmas que ocurrieron en un solo día** están marcadas con una **línea vertical punteada** en el día correspondiente.
            """,
            """
            Las alarmas con menos de 100 activaciones se han agrupado en una categoría denominada **‘Others’**. Esta agrupación permite mantener el gráfico limpio y enfocado en las alarmas con un **mayor número de activaciones**.
            """
        ]

        for p in graph_explanation:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_chart_histogram(self, alarm_dates, alarm_names, counts) -> str:
        plt.figure(figsize=(18, 10))
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        data = pd.DataFrame({
            'Alarm Date': alarm_dates,
            'Alarm Name': alarm_names,
            'Counts': counts
        })

        for i, (name, group) in enumerate(data.groupby('Alarm Name')):
            total_events = group['Counts'].sum()
            color = colors[i % len(colors)]
            plt.plot(group['Alarm Date'], group['Counts'], label=f"{name} - Total: ({total_events})", color=color)

            max_count = group['Counts'].max()
            max_date = group['Alarm Date'][group['Counts'].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=color)

            if len(group) == 1:
                plt.axvline(x=group['Alarm Date'].iloc[0], color=color, linestyle='dashed')

        plt.yticks(np.arange(0, data['Counts'].max(), step=300))
        plt.xticks(pd.date_range(start=data['Alarm Date'].min(), end=data['Alarm Date'].max(), freq='3D'))
        plt.legend()

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def stacked_bar_chart_by_alarm_type(self):
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de barras apiladas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date']).dt.floor('d')
        if 'Counts' not in df.columns:
            df['Counts'] = 1

        top_alarms = df.groupby('Alarm Name')['Counts'].sum().sort_values(ascending=False).head(10).index
        df = df[df['Alarm Name'].isin(top_alarms)]

        pivot_df = df.pivot_table(index='Alarm Date', columns='Alarm Name', values='Counts', aggfunc='sum', fill_value=0)

        figure_src = self._draw_stacked_bar_chart(pivot_df)

        elements = ElementList()
        elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
        elements += Paragraph("Activaciones de Alarmas por Fecha", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        description = [
            """
            Este gráfico de barras apiladas muestra la cantidad de activaciones de diferentes alarmas a lo largo del tiempo. Para mantener el gráfico claro y manejable, hemos seleccionado las diez alarmas con el mayor número total de activaciones durante todo el período analizado.
            """,
            """
            El eje **x** muestra las fechas, mientras que el eje **y** representa el número total de activaciones. Este enfoque facilita la comparación de las alarmas más frecuentes a lo largo del tiempo.
            """,
            """
            Utilizando colores diferentes para cada tipo de alarma, el gráfico ayuda a identificar patrones y picos en la activación de alarmas. Las diez alarmas más significativas se incluyen para destacar las tendencias más importantes.
            """
        ]

        for p in description:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_stacked_bar_chart(self, pivot_df: pd.DataFrame) -> str:
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        ax = pivot_df.plot(kind='bar', stacked=True, figsize=(18, 10), color=colors[:len(pivot_df.columns)])
        plt.title("Activaciones de Alarmas por Fecha")
        plt.xlabel("Fecha")
        plt.ylabel("Número de Activaciones")
        plt.legend(title="Nombre de la Alarma")

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def stacked_bar_chart_by_alarm_status(self):
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de barras apiladas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])

        # Excluir las alarmas con estado "New" y "Open Alarm"
        df_filtered = df[~df['Alarm Status'].isin(['New', 'Open Alarm'])]

        # Agrupar los datos por 'Alarm Name' y 'Alarm Status'
        alarms = df_filtered.groupby(['Alarm Name', 'Alarm Status']).size().unstack(fill_value=0)

        figure_src = self._draw_stacked_bar_chart_by_alarm_status(alarms)

        elements = ElementList()
        elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
        elements += Paragraph("Distribución de Alarmas por Tipo y Estado", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        description = [
            """
            Este gráfico de barras apiladas muestra la distribución de diferentes tipos de alarmas según su estado. Las alarmas con estado "New" y "Open Alarm" han sido excluidas para una mejor claridad.
            """,
            """
            El eje **x** representa los diferentes tipos de alarmas, mientras que el eje **y** muestra el número total de cada estado de alarma. Este gráfico ayuda a visualizar la proporción de cada estado para diferentes alarmas.
            """,
            """
            Utilizando colores diferentes para cada estado de alarma, el gráfico facilita la identificación de las alarmas que están en estados críticos o resueltos, destacando las tendencias más importantes en la gestión de alarmas.
            """
        ]

        for p in description:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_stacked_bar_chart_by_alarm_status(self, alarms: pd.DataFrame) -> str:
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        ax = alarms.plot(kind='bar', stacked=True, figsize=(18, 10), color=colors[:len(alarms.columns)])
        plt.title("Distribución de Alarmas por Tipo y Estado")
        plt.xlabel("Tipo de Alarma")
        plt.ylabel("Número de Alarmas")
        plt.legend(title="Estado de la Alarma")

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def heatmap_alarms_by_day_and_hour(self):
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el mapa de calor.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])
        df['Day'] = df['Alarm Date'].dt.day_name()
        df['Hour'] = df['Alarm Date'].dt.hour

        # Asegurarse de que 'Counts' existe
        if 'Counts' not in df.columns:
            df['Counts'] = 1  # Suponiendo que cada fila representa una activación de alarma

        pivot_df = df.pivot_table(index='Day', columns='Hour', values='Counts', aggfunc='sum', fill_value=0)

        figure_src = self._draw_heatmap(pivot_df)

        elements = ElementList()
        elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
        elements += Paragraph("Mapa de Calor de Activaciones de Alarmas por Día y Hora", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        description = [
            """
            Este mapa de calor muestra la frecuencia de activaciones de alarmas en diferentes días y horas, permitiendo identificar patrones temporales de activaciones. Al agrupar las activaciones por días de la semana y horas del día, se pueden observar los momentos de mayor actividad.
            """,
            """
            El eje **x** representa las horas del día, dividiendo las 24 horas en intervalos de una hora. El eje **y** muestra los días de la semana, desde el lunes hasta el domingo. Los colores en el mapa indican la cantidad de activaciones: los colores más oscuros representan una mayor frecuencia de activaciones, mientras que los colores más claros indican una menor frecuencia.
            """,
            """
            Este gráfico es útil para identificar tendencias diarias y semanales en las activaciones de alarmas. Por ejemplo, puede ayudar a detectar si hay ciertos días de la semana y horas específicas en las que las alarmas son más frecuentes, lo que podría indicar patrones de comportamiento o eventos recurrentes que requieren atención.
            """
        ]

        for p in description:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_heatmap(self, pivot_df) -> str:
        plt.figure(figsize=(18, 10))
        sns.heatmap(pivot_df, cmap='coolwarm', annot=True, fmt='d')
        plt.title("Mapa de Calor de Activaciones de Alarmas por Día y Hora")
        plt.xlabel("Hora del Día")
        plt.ylabel("Día de la Semana")

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def scatter_plot_time_to_detection(self):
        df = self.db.get_alarm_durations_cached()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de dispersión.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Duration'] = df['TTD'].astype(float)
        alarm_names = df['AlarmName'].unique()
        elements = ElementList()

        for i in range(0, len(alarm_names), 10):
            subset_alarm_names = alarm_names[i:i+10]
            subset_df = df[df['AlarmName'].isin(subset_alarm_names)].copy()
            figure_src = self._draw_scatter_plot(subset_df)

            elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
            elements += Paragraph("Duración de Activaciones de Alarmas (Time to Detection)", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        description = [
            """
            Este gráfico de dispersión muestra la duración de cada activación de alarma en términos de Tiempo hasta la Detección (TTD). El TTD se refiere al tiempo que transcurre desde que se genera una alarma hasta que se inicia su investigación, proporcionando una visión clara de la variabilidad y la magnitud de las duraciones de las alarmas.
            """,
            """
            En este gráfico, el eje **x** representa las fechas de activación de las alarmas, permitiendo visualizar cómo se distribuyen las activaciones a lo largo del tiempo. El eje **y** muestra la duración en minutos, calculada dividiendo los valores de TTD (originalmente en segundos) por 60. Cada punto en el gráfico representa una activación individual de una alarma. Los colores de los puntos diferencian los distintos tipos de alarmas, facilitando la identificación visual de patrones específicos relacionados con cada tipo de alarma.
            """
        ]

        for p in description:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_scatter_plot(self, df) -> str:
        df['Duration'] = df['Duration'].astype(float) / 60.0  # Explicitly cast to float

        plt.figure(figsize=(18, 10))
        sns.scatterplot(data=df, x='AlarmDate', y='Duration', hue='AlarmName', style='AlarmName')

        plt.title("Duración de Activaciones de Alarmas (Time to Detection)")
        plt.xlabel("Fecha de Activación")
        plt.ylabel("Duración (minutos)")
        plt.legend(title="Nombre de la Alarma")

        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def box_plot_time_to_detection(self):
        df = self.db.get_alarm_durations_cached()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de caja.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Duration'] = df['TTD'].astype(float) / 60.0
        alarm_names = df['AlarmName'].unique()
        elements = ElementList()

        for i in range(0, len(alarm_names), 10):
            subset_alarm_names = alarm_names[i:i+10]
            subset_df = df[df['AlarmName'].isin(subset_alarm_names)].copy()
            figure_src = self._draw_box_plot(subset_df)

            elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
            elements += Paragraph("Distribución de Duraciones de Activaciones de Alarmas (Time to Detection)", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        description = [
            """
            Este diagrama de caja proporciona una representación estadística de la distribución de las duraciones de las activaciones de alarmas, medidas en términos de Time to Detection (TTD). El TTD se calcula como el intervalo de tiempo entre la generación de una alarma y el inicio de su investigación.
            """,
            """
            En este gráfico, el eje **x** clasifica los diferentes tipos de alarmas, permitiendo una comparación directa entre ellas. El eje **y** muestra la duración en minutos, obtenida dividiendo los valores de TTD (originalmente en segundos) por 60. Cada caja en el diagrama representa el rango intercuartílico (IQR) de las duraciones, delimitado por el primer y tercer cuartil (Q1 y Q3), con una línea en el interior que indica la mediana. 
            """,
            """
            El IQR es una medida de la dispersión de los datos que describe el rango donde se encuentra el 50% central de los valores. Los extremos de las "bigotes" se extienden hasta 1.5 veces el IQR desde los cuartiles, y los puntos fuera de estos límites se consideran valores atípicos, que se destacan en el gráfico. Este diagrama es útil para identificar la dispersión, simetría y presencia de valores atípicos en las duraciones de las activaciones de alarmas para cada tipo de alarma.
            """
        ]

        for p in description:
            elements += Paragraph(self.replace_bold_with_font(p), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        return elements

    def _draw_box_plot(self, df) -> str:
        df['Duration'] = df['Duration'].astype(float)

        plt.figure(figsize=(18, 10))
        sns.boxplot(data=df, x='AlarmName', y='Duration')

        plt.title("Distribución de Duraciones de Activaciones de Alarmas (Time to Detection)")
        plt.xlabel("Nombre de la Alarma")
        plt.ylabel("Duración (minutos)")
        plt.xticks(rotation=90)

        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        return output

    def replace_bold_with_font(self, text):
        import re
        return re.sub(r'\*\*(.*?)\*\*', r'<font face="Arial-Narrow-Bold">\1</font>', text)


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import seaborn as sns
from uuid import uuid4 as v4
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import cm
from modules.template.theme import ParagraphStyles
from utils import ElementList
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from modules.components import Components

class Draw:
    def __init__(self, charts: 'Charts') -> None:
        self.charts = charts

    def chart_histogram(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> str:
        """
        Generate a histogram chart from the given DataFrame.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        category_col (str): The name of the column to categorize the data.

        Returns:
        str: The file path of the saved chart image.
        """
        plt.figure(figsize=(18, 10))
        colors = self._generate_colors(df[category_col].nunique())

        for i, (name, group) in enumerate(df.groupby(category_col)):
            total_events = group[y_col].sum()
            color = colors[i % len(colors)]
            plt.plot(group[x_col], group[y_col], label=f"{name} - Total: ({total_events})", color=color)

            max_count = group[y_col].max()
            max_date = group[x_col][group[y_col].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=color)

            if len(group) == 1:
                plt.axvline(x=group[x_col].iloc[0], color=color, linestyle='dashed')

        plt.yticks(np.arange(0, df[y_col].max(), step=300))
        plt.xticks(pd.date_range(start=df[x_col].min(), end=df[x_col].max(), freq='3D'))
        plt.legend()

        return self._save_chart()

    def stacked_bar_chart(self, pivot_df: pd.DataFrame, x_col: str) -> str:
        colors = self._generate_colors(len(pivot_df.columns))

        ax = pivot_df.plot(kind='bar', stacked=True, figsize=(18, 10), color=colors)
        plt.xlabel(x_col)
        plt.ylabel("Número de Activaciones")
        plt.legend(title="Nombre de la Alarma")

        return self._save_chart()

    def heatmap_chart(self, pivot_df: pd.DataFrame, xlabel: str = "Hora del Día", ylabel: str = "Día de la Semana") -> str:
        plt.figure(figsize=(18, 10))
        sns.heatmap(pivot_df, cmap='coolwarm', annot=True, fmt='d')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        return self._save_chart()
    
    def scatter_chart(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> str:
        df[y_col] = df[y_col].astype(float) / 60.0

        plt.figure(figsize=(18, 10))
        sns.scatterplot(data=df, x=x_col, y=y_col, hue=category_col, style=category_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title=category_col)

        return self._save_chart()

    def box_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> str:
        df[y_col] = df[y_col].astype(float)

        plt.figure(figsize=(18, 10))
        sns.boxplot(data=df, x=x_col, y=y_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=90)

        return self._save_chart()
    
    def bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, rotate: bool = True) -> str:
        plt.figure(figsize=(12, 8))
        
        sns.barplot(x=df[x_col], y=df[y_col], hue=df[x_col], palette=self._generate_colors(len(df)), dodge=False)
        
        if rotate:
            plt.xticks(rotation=45, ha='right')

        plt.xlabel(x_col)
        plt.ylabel(y_col)

        return self._save_chart()

    def pareto_chart(self, df: pd.DataFrame, value_col: str, category_col: str) -> str:
        df = df.sort_values(by=value_col, ascending=False).reset_index(drop=True)
        df['cum_percentage'] = df[value_col].cumsum() / df[value_col].sum() * 100

        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(df[category_col], df[value_col], color='C0')
        ax2 = ax.twinx()
        ax2.plot(df[category_col], df['cum_percentage'], color='C1', marker='D', ms=7)
        ax2.yaxis.set_major_formatter(ticker.PercentFormatter())

        # Set ticks and rotate x-axis labels
        ax.set_xticks(range(len(df[category_col])))
        ax.set_xticklabels(df[category_col], rotation=45, ha='right')

        # Set labels
        ax.set_ylabel('Count')
        ax2.set_ylabel('Cumulative Percentage')

        # Add gridlines
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Show plot
        plt.tight_layout()

        return self._save_chart()
        
    def bubble_chart_attack_impact(self, df: pd.DataFrame) -> str:
        plt.figure(figsize=(18, 10))
        bubble_size = df['severity'].apply(lambda x: 100 if x == 'critical' else 50)
        
        sns.scatterplot(
            data=df,
            x='impactedLocationName',
            y='count',
            size=bubble_size,
            hue='severity',
            palette='coolwarm',
            sizes=(50, 500),
            alpha=0.7,
            edgecolor='k'
        )
        plt.title('Bubble Chart for Attack Impact')
        plt.xlabel('Impacted Location')
        plt.ylabel('Count of Attacks')
        plt.xticks(rotation=45)
        plt.legend(title='Severity')

        return self._save_chart()

    def box_plot_attack_frequency(self, df: pd.DataFrame) -> str:
        plt.figure(figsize=(18, 10))
        
        sns.boxplot(
            data=df,
            x='msgSourceTypeName',
            y='count'
        )
        plt.title('Box Plot for Attack Frequency by Source Type')
        plt.xlabel('Message Source Type')
        plt.ylabel('Count of Attacks')
        plt.xticks(rotation=45)

        return self._save_chart()
        
    def pie_chart_attack_direction(self, df: pd.DataFrame) -> str:
        plt.figure(figsize=(18, 10))
        
        attack_counts = df['directionName'].value_counts()
        attack_counts.plot.pie(
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette('husl', len(attack_counts)),
            wedgeprops={'linewidth': 1, 'edgecolor': 'black'}
        )
        plt.title('Pie Chart for Attack Direction')
        plt.ylabel('')

        return self._save_chart()

    def time_series_attacks_by_priority(self, df: pd.DataFrame) -> str:
        df['normalDate'] = pd.to_datetime(df['normalDate'])
        df['Date'] = df['normalDate'].dt.date

        plt.figure(figsize=(18, 10))
        for priority in df['priority'].unique():
            subset = df[df['priority'] == priority]
            trends_df = subset.groupby('Date')['count'].sum().reset_index()
            plt.plot(trends_df['Date'], trends_df['count'], marker='o', label=f'Priority {priority}')
        
        plt.xlabel('Date')
        plt.ylabel('Number of Events')
        plt.title('Time Series Analysis of Attacks by Priority')
        plt.legend()
        plt.grid(True)

        return self._save_chart()

    def _generate_colors(self, n: int) -> List[str]:
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8', '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']
        return sns.color_palette('husl', n)

    def _save_chart(self) -> str:
        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output), 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        return output


class Charts:
    def __init__(self, components: 'Components') -> None:
        self.components = components
        self.theme = components.theme
        self.db = components.db
        self.pkg = components.pkg
        self.draw = Draw(self)

    def generate_report_elements(self, title: str, description: List[str], figure_src: str) -> ElementList:
        elements = ElementList()
        elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")
        elements += Paragraph(title, self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        for desc in description:
            elements += Paragraph(self.replace_bold_with_font(desc), self.theme.get_style(ParagraphStyles.NR_TEXTO_1))
        
        return elements

    def trends_in_alarm_activation_graph(self) -> ElementList:
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el histograma.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date']).dt.floor('d')
        by_date_and_name = df.groupby(['Alarm Date', 'Alarm Name']).size().reset_index(name='Counts')

        # Filter and group "Others"
        threshold = 100
        less_than = by_date_and_name[by_date_and_name['Counts'] < threshold]
        others = less_than.groupby('Alarm Date')['Counts'].sum().reset_index()
        others['Alarm Name'] = 'Others'
        by_date_and_name = by_date_and_name[by_date_and_name['Counts'] >= threshold]
        by_date_and_name = pd.concat([by_date_and_name, others], ignore_index=True)

        figure_src = self.draw.chart_histogram(
            by_date_and_name, 
            x_col='Alarm Date', 
            y_col='Counts', 
            category_col='Alarm Name'
        )

        description = [
            "Este gráfico proporciona una visualización detallada de la evolución temporal de diferentes alarmas...",
            "El eje **x** muestra las fechas, con **marcas cada tres días**. El eje **y** representa el número...",
            "Las alarmas con menos de 100 activaciones se han agrupado en una categoría denominada **‘Others’**..."
        ]

        return self.generate_report_elements("Tendencias en la Activación de Alarmas", description, figure_src)

    def stacked_bar_chart_by_alarm_type(self) -> ElementList:
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de barras apiladas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date']).dt.floor('d')
        if 'Counts' not in df.columns:
            df['Counts'] = 1

        top_alarms = df.groupby('Alarm Name')['Counts'].sum().sort_values(ascending=False).head(10).index
        df = df[df['Alarm Name'].isin(top_alarms)]

        pivot_df = df.pivot_table(index='Alarm Date', columns='Alarm Name', values='Counts', aggfunc='sum', fill_value=0)
        figure_src = self.draw.stacked_bar_chart(pivot_df, x_col='Alarm Date')

        description = [
            "Este gráfico de barras apiladas muestra la cantidad de activaciones de diferentes alarmas a lo largo del tiempo...",
            "El eje **x** muestra las fechas, mientras que el eje **y** representa el número total de activaciones...",
            "Utilizando colores diferentes para cada tipo de alarma, el gráfico ayuda a identificar patrones y picos..."
        ]

        return self.generate_report_elements("Activaciones de Alarmas por Fecha", description, figure_src)

    def stacked_bar_chart_by_alarm_status(self) -> ElementList:
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de barras apiladas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])
        df_filtered = df[~df['Alarm Status'].isin(['New', 'Open Alarm'])]

        alarms = df_filtered.groupby(['Alarm Name', 'Alarm Status']).size().unstack(fill_value=0)
        figure_src = self.draw.stacked_bar_chart(alarms, x_col='Alarm Name')

        description = [
            "Este gráfico de barras apiladas muestra la distribución de diferentes tipos de alarmas según su estado...",
            "El eje **x** representa los diferentes tipos de alarmas, mientras que el eje **y** muestra el número total...",
            "Utilizando colores diferentes para cada estado de alarma, el gráfico facilita la identificación de las alarmas..."
        ]

        return self.generate_report_elements("Distribución de Alarmas por Tipo y Estado", description, figure_src)

    def heatmap_alarms_by_day_and_hour(self) -> ElementList:
        df = self.db.get_alarm_details_by_entity()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el mapa de calor.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])
        df['Day'] = df['Alarm Date'].dt.day_name()
        df['Hour'] = df['Alarm Date'].dt.hour
        df['Counts'] = df.get('Counts', 1)

        pivot_df = df.pivot_table(index='Day', columns='Hour', values='Counts', aggfunc='sum', fill_value=0)
        figure_src = self.draw.heatmap_chart(pivot_df)

        description = [
            "Este mapa de calor muestra la frecuencia de activaciones de alarmas en diferentes días y horas...",
            "El eje **x** representa las horas del día, dividiendo las 24 horas en intervalos de una hora...",
            "Este gráfico es útil para identificar tendencias diarias y semanales en las activaciones de alarmas..."
        ]

        return self.generate_report_elements("Mapa de Calor de Activaciones de Alarmas por Día y Hora", description, figure_src)

    def scatter_plot_time_to_detection(self) -> ElementList:
        df = self.db.get_alarm_durations_cached()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de dispersión.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Duration'] = df['TTD'].astype(float)
        alarm_names = df['AlarmName'].unique()
        elements = ElementList()

        description = [
            "Este gráfico de dispersión muestra la duración de cada activación de alarma en términos de Tiempo hasta la Detección (TTD)...",
            "En este gráfico, el eje **x** representa las fechas de activación de las alarmas...",
            "Los colores de los puntos diferencian los distintos tipos de alarmas, facilitando la identificación visual de patrones..."
        ]

        for i in range(0, len(alarm_names), 10):
            subset_alarm_names = alarm_names[i:i+10]
            subset_df = df[df['AlarmName'].isin(subset_alarm_names)].copy()
            figure_src = self.draw.scatter_chart(subset_df, x_col='AlarmDate', y_col='Duration', category_col='AlarmName')
            
            elements += self.generate_report_elements(
                title="Duración de Activaciones de Alarmas (Time to Detection)",
                description=description,
                figure_src=figure_src
            )
        
        return elements

    def box_plot_time_to_detection(self) -> ElementList:
        df = self.db.get_alarm_durations_cached()
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de caja.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['Duration'] = df['TTD'].astype(float) / 60.0
        alarm_names = df['AlarmName'].unique()
        elements = ElementList()

        description = [
            "Este diagrama de caja proporciona una representación estadística de la distribución de las duraciones...",
            "En este gráfico, el eje **x** clasifica los diferentes tipos de alarmas...",
            "Los extremos de las 'bigotes' se extienden hasta 1.5 veces el IQR desde los cuartiles..."
        ]

        for i in range(0, len(alarm_names), 10):
            subset_alarm_names = alarm_names[i:i+10]
            subset_df = df[df['AlarmName'].isin(subset_alarm_names)].copy()
            figure_src = self.draw.box_chart(subset_df, x_col='AlarmName', y_col='Duration')
            
            elements += self.generate_report_elements(
                title="Distribución de Duraciones de Activaciones de Alarmas (Time to Detection)",
                description=description,
                figure_src=figure_src
            )
        
        return elements

    def bar_chart_top_attackers(self) -> ElementList:
        df = next((q.run() for q in self.pkg if q._id == "cdc64feb-bcd3-4675-be78-44f8d6f2af9d"), pd.DataFrame())

        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de barras.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.bar_chart(df, x_col='originIp', y_col='count')

        description = [
            "Este gráfico de barras muestra el número de ataques desde cada IP de origen.",
            "Las barras permiten una comparación fácil y directa del número de ataques de los diferentes atacantes."
        ]

        return self.generate_report_elements("Top Atacantes - Gráfico de Barras", description, figure_src)

    def pareto_chart_top_attackers(self, df: pd.DataFrame, title: str, description: list[str]) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de Pareto.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.pareto_chart(df, value_col='count', category_col='originIp')

        return self.generate_report_elements(title, description, figure_src)

    # --- Bloque de Nuevos Gráficos ---

    def heatmap_chart_by_severity_and_location(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el mapa de calor.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        # Pivotar el DataFrame para el heatmap
        pivot_df = df.pivot_table(
            index='impactedLocationName',
            columns='severity',
            values='count',
            aggfunc='sum',
            fill_value=0
        )

        # Generar el gráfico de heatmap
        figure_src = self.draw.heatmap_chart(pivot_df, "Severity", "Location")

        description = [
            "Este mapa de calor muestra la distribución de eventos por severidad y ubicación afectada.",
            "El eje **x** representa los diferentes niveles de severidad de los eventos.",
            "El eje **y** representa las ubicaciones afectadas.",
            "Los colores en el mapa indican el número de eventos, con colores más oscuros representando mayor cantidad de eventos."
        ]

        return self.generate_report_elements("Mapa de Calor de Eventos por Severidad y Ubicación", description, figure_src)

    def line_chart_trends_by_date(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de líneas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        df['normalDate'] = pd.to_datetime(df['normalDate'])
        df['Date'] = df['normalDate'].dt.date
        trends_df = df.groupby('Date')['count'].sum().reset_index()

        plt.figure(figsize=(18, 10))
        plt.plot(trends_df['Date'], trends_df['count'], marker='o')
        plt.xlabel("Fecha")
        plt.ylabel("Número de Eventos")
        plt.title("Tendencias de Eventos por Fecha")
        plt.grid(True)

        figure_src = self.draw._save_chart()

        description = [
            "Este gráfico de líneas muestra la tendencia de los eventos a lo largo del tiempo.",
            "El eje **x** representa las fechas y el eje **y** muestra el número de eventos.",
            "Es útil para identificar picos y patrones en la ocurrencia de eventos críticos."
        ]

        return self.generate_report_elements("Tendencias de Eventos por Fecha", description, figure_src)

    def bubble_chart_attack_impact(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de burbujas.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.bubble_chart_attack_impact(df)
        description = [
            "Este gráfico de burbujas muestra la relación entre la severidad de los ataques, su cuenta, y las ubicaciones afectadas.",
            "El tamaño de las burbujas representa la severidad de los ataques, con burbujas más grandes indicando mayor severidad.",
            "Los colores de las burbujas indican la severidad de los ataques, ayudando a identificar las ubicaciones más impactadas."
        ]

        return self.generate_report_elements("Gráfico de Burbujas de Impacto de Ataques", description, figure_src)

    def box_plot_attack_frequency(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de caja.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.box_plot_attack_frequency(df)
        description = [
            "Este diagrama de caja muestra la distribución de la frecuencia de ataques desde diferentes tipos de fuente.",
            "Cada caja representa el rango intercuartílico (IQR) y los bigotes indican el rango de los datos.",
            "Los puntos fuera de los bigotes se consideran valores atípicos."
        ]

        return self.generate_report_elements("Gráfico de Caja de Frecuencia de Ataques por Tipo de Fuente", description, figure_src)


    def pie_chart_attack_direction(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de pastel.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.pie_chart_attack_direction(df)
        description = [
            "Este gráfico de pastel muestra la proporción de ataques según su dirección (interno vs. externo).",
            "Las secciones del pastel representan las diferentes direcciones de los ataques, ayudando a visualizar la distribución."
        ]

        return self.generate_report_elements("Gráfico de Pastel para la Dirección de Ataques", description, figure_src)

    def time_series_attacks_by_priority(self, df: pd.DataFrame) -> ElementList:
        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el gráfico de series temporales.", self.theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        figure_src = self.draw.time_series_attacks_by_priority(df)
        description = [
            "Este gráfico de líneas muestra la tendencia de los ataques a lo largo del tiempo, categorizados por prioridad.",
            "El eje **x** representa las fechas y el eje **y** muestra el número de eventos.",
            "Es útil para identificar picos y patrones en la ocurrencia de eventos críticos."
        ]

        return self.generate_report_elements("Análisis de Series Temporales de Ataques por Prioridad", description, figure_src)


    def replace_bold_with_font(self, text: str) -> str:
        import re
        return re.sub(r'\*\*(.*?)\*\*', r'<font face="Arial-Narrow-Bold">\1</font>', text)


import pandas as pd
from src.utils import ElementList
from .canvas import Canvas
from src.themes import theme
from src.components import Bar, Cover, Line
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from src.databases import MSQLServer
    from src.app import Config
    from src.reports.skeleton import Report

class GeneralTemplate():
    canvasmaker: Canvas
    elements: ElementList

    def __init__(self, report: 'Report', queries, database: 'MSQLServer', metadata: dict, config: 'Config') -> None:
        self.report, self.queries, self.db, self.metadata, self.config = report, queries, database, metadata, config
        Canvas.metadata = metadata
        self.canvasmaker = Canvas
        self.elements = ElementList()
        self.theme = self.report.theme
        self.style = self.theme.get_style
        self.paragraph_styles = theme.ParagraphStyles

    def _process_alarm_data(self):
        df = self.db.get_alarms_information()

        # Convertir la columna 'AlarmDate' a tipo datetime y agrupar los datos
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')
        df = df.groupby(['AlarmDate', 'AlarmRuleName', 'AlarmPriority'], observed=False).size().reset_index(name='Counts')

        # Filtrar y agrupar las alarmas de baja prioridad
        priority = 50
        low_priority = df[df['AlarmPriority'] < priority].groupby('AlarmDate', observed=False)['Counts'].sum().reset_index()
        low_priority['AlarmRuleName'] = 'Low Priority'

        # Filtrar las alarmas de alta prioridad y concatenar con las de baja prioridad
        df = df[df['AlarmPriority'] >= priority]
        df = pd.concat([df, low_priority], ignore_index=True)

        return df

    def plot_alarm_trends(self):
        df = self._process_alarm_data()

        # Graficar todos los datos sin chunks
        full_figure = Line(
            df,
            x_col='AlarmDate',
            y_col='Counts',
            category_col='AlarmRuleName',
            title='Histograma de Activación de Alarmas (Completo)',
            show_legend=True,
            show_max_annotate=True,
            axies_labels=True,
        ).plot()

        return [full_figure]

    def plot_alarm_trends_in_chunks(self):
        df = self._process_alarm_data()

        # Agrupar por 'AlarmRuleName' y contar
        alarm_counts = df.groupby('AlarmRuleName', observed=False)['Counts'].sum().reset_index()
        alarm_counts = alarm_counts.sort_values(by='Counts', ascending=False)

        # Dividir los nombres de las alarmas en chunks de 10
        chunk_size = 10
        alarm_names_chunks = [alarm_counts.iloc[i:i + chunk_size]['AlarmRuleName'].tolist() for i in range(0, len(alarm_counts), chunk_size)]

        figures = []
        for chunk in alarm_names_chunks:
            chunk_df = df[df['AlarmRuleName'].isin(chunk)].sort_values(by='AlarmDate')
            figure = Line(
                chunk_df,
                x_col='AlarmDate',
                y_col='Counts',
                category_col='AlarmRuleName',
                title='Histograma de Activación de Alarmas (Chunk)',
                show_legend=True,
                show_max_annotate=True,
                axies_labels=True,
            )
            figures.append(figure.plot())

        # Devolver las figuras generadas
        return figures

    def plot_top_alarms(self):
        df = self.db.get_alarms_information()
        df = df.groupby('AlarmRuleName', observed=False).size().reset_index(name='Count')
        df = df.sort_values(by='Count', ascending=False)

        bar = Bar(df, x_col='AlarmRuleName', y_col='Count', show_xticks=False, show_legend=True)
        return [bar.plot()]

    def plot_priority_levels(self):
        df = self.db.get_alarms_information()

        # Manejar los valores NaN en 'AlarmPriority'
        df = df.dropna(subset=['AlarmPriority'])

        # Convertir la columna 'AlarmDate' a tipo datetime
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')

        # Definir las categorías de prioridad
        df['PriorityLevel'] = pd.cut(
            df['AlarmPriority'],
            bins=[-1, 50, 75, 100],
            labels=['Low Priority', 'Medium Priority', 'High Priority']
        )

        # Agrupar y contar las alarmas por nivel de prioridad
        df = df.groupby(['AlarmDate', 'PriorityLevel'], observed=False).size().reset_index(name='Counts')

        # Graficar los niveles de prioridad
        figure = Line(
            df,
            x_col='AlarmDate',
            y_col='Counts',
            category_col='PriorityLevel',
            title='Histograma de Activación de Alarmas por Nivel de Prioridad',
            show_legend=True,
            show_max_annotate=True,
            axies_labels=True,
        ).plot()

        return [figure]

    def _format_date(self, date: datetime) -> str:
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _prepare_text(self, today: str, start: str, end: str, client_name: str) -> str:
        text = f"""
            **Reporte preparado para:** {client_name}<br/>
            **Fecha de creación:** {today}<br/>
            **Periodo del reporte:** Entre {start} y {end}<br/>
            **Preparado por:** {self.metadata.get("author", "Netready Solutions")}
        """
        return self.theme.replace_bold_with_font(text)

    def run(self):
        today = self._format_date(datetime.now())
        start, end = map(self._format_date, self.config.date_range)

        client_name, client_logo = self.config.client_details

        text = self._prepare_text(today, start, end, client_name)
        footer = f"© {datetime.now().year} Soluciones Netready, C.A. All Rights Reserved."

        self.elements += Cover(self.metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, self.theme).render()
        self.elements += self.plot_top_alarms()
        self.elements += self.plot_alarm_trends()
        self.elements += self.plot_alarm_trends_in_chunks()
        self.elements += self.plot_priority_levels()
        
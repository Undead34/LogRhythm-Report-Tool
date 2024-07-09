import pandas as pd
from src.utils import ElementList
from .canvas import Canvas
from typing import TYPE_CHECKING
from datetime import datetime
from reportlab.lib.units import cm
from src.themes import theme
from src.components import Bar, Cover, Line, PageBreak, Paragraph, Table, ListElement

if TYPE_CHECKING:
    from src.databases import MSQLServer
    from src.app import Config
    from src.reports.skeleton import Report

class GeneralTemplate:
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
        self.tables_styles = theme.CustomTableStyles

    def _process_alarm_data(self):
        df = self.db.get_alarms_information()
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')
        df = df.groupby(['AlarmDate', 'AlarmRuleName', 'AlarmPriority'], observed=False).size().reset_index(name='Counts')

        priority = 50
        low_priority = df[df['AlarmPriority'] < priority].groupby('AlarmDate', observed=False)['Counts'].sum().reset_index()
        low_priority['AlarmRuleName'] = 'Low Priority'

        df = df[df['AlarmPriority'] >= priority]
        df = pd.concat([df, low_priority], ignore_index=True)

        return df

    def plot_alarm_trends(self):
        df = self._process_alarm_data()
        full_figure = Line(
            df,
            x_col='AlarmDate',
            y_col='Counts',
            category_col='AlarmRuleName',
            title='Histograma de Activación de Alarmas (Completo)',
            show_legend=True,
            show_max_annotate=True,
            axis_labels=True,
        ).plot()

        return [full_figure]

    def plot_alarm_trends_in_chunks(self):
        df = self._process_alarm_data()
        alarm_counts = df.groupby('AlarmRuleName', observed=False)['Counts'].sum().reset_index()
        alarm_counts = alarm_counts.sort_values(by='Counts', ascending=False)

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
                axis_labels=True,
            )
            figures.append(figure.plot())

        return figures

    def plot_top_alarms(self):
        df = self.db.get_alarms_information()
        df = df.groupby('AlarmRuleName', observed=False).size().reset_index(name='Count')
        df = df.sort_values(by='Count', ascending=False)

        bar = Bar(df, x_col='AlarmRuleName', y_col='Count', show_xticks=False, show_legend=True)
        return [bar.plot()]

    def plot_priority_levels(self):
        df = self.db.get_alarms_information()
        df = df.dropna(subset=['AlarmPriority'])
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')

        df['PriorityLevel'] = pd.cut(
            df['AlarmPriority'],
            bins=[-1, 50, 75, 100],
            labels=['Low Priority', 'Medium Priority', 'High Priority']
        )

        df = df.groupby(['AlarmDate', 'PriorityLevel'], observed=False).size().reset_index(name='Counts')

        figure = Line(
            df,
            x_col='AlarmDate',
            y_col='Counts',
            category_col='PriorityLevel',
            title='Histograma de Activación de Alarmas por Nivel de Prioridad',
            show_legend=True,
            show_max_annotate=True,
            axis_labels=True,
        ).plot()

        return [figure]

    def sla_compliance_indicators(self):
        df = self.db.get_alarms_information()
        df = df.loc[:, ["MsgClassName", "AlarmRuleName"]]
        table = Table(df, table_style_name=self.tables_styles.DEFAULT.value)
        return table.create_pdf_table(self.theme)

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

    def add_introduction(self):
        elements = ElementList()
        elements += Paragraph("Introducción".upper(), self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph("1. Objetivo del Informe", self.style(self.paragraph_styles.TITLE_2))

        paragraph_1 = self.theme.replace_bold_with_font(
            """
            **Propósito**: El propósito de este informe es proporcionar una visión detallada y automatizada del estado del Sistema de Gestión de Información y Eventos de Seguridad (SIEM), destacando los aspectos clave relacionados con la seguridad, el rendimiento y la conformidad.
            """
        )
        elements += Paragraph(paragraph_1, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        paragraph_2 = self.theme.replace_bold_with_font(
            """
            **Alcance**: Este informe cubre la actividad del SIEM durante el periodo especificado,
                        incluyendo la identificación de atacantes, vulnerabilidades, alarmas, violaciones de cumplimiento,
                        fallas operativas, violaciones de auditoría, detalles de logs, estadísticas de componentes y resúmenes automáticos.
            """
        )
        elements += Paragraph(paragraph_2, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        paragraph_3 = self.theme.replace_bold_with_font(
            """
             **Metodología**: Los datos presentados en este informe han sido recopilados y analizados utilizando herramientas automatizadas
                que integran y correlacionan información de múltiples fuentes. Los gráficos y tablas incluidos son el resultado
                de análisis estadísticos diseñados para resaltar tendencias significativas y puntos de atención críticos.
            """
        )
        elements += Paragraph(paragraph_3, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        paragraph_4 = self.theme.replace_bold_with_font(
            """
                **Estructura del Informe**: Este informe se divide en varias secciones clave:
            """
        )
        elements += Paragraph(paragraph_4, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        sections = [
            "**Indicadores de cumplimiento de SLA y Tiempos de Gestión**: Un análisis detallado de los indicadores de nivel de servicio (SLA) y tiempos de respuesta para la gestión de incidentes y eventos.",
            "**Análisis de Eventos**: Un desglose de los eventos capturados por el SIEM, categorizados por tipo, gravedad y fuente.",
            "**Detección de Amenazas**: Información sobre amenazas detectadas, incluyendo atacantes identificados, métodos de ataque y medidas de mitigación implementadas.",
            "**Conformidad y Auditoría**: Evaluación del cumplimiento de políticas de seguridad y auditorías realizadas durante el periodo.",
            "**Recomendaciones**: Sugerencias para mejorar la postura de seguridad basada en los hallazgos del análisis."
        ]

        sections = [Paragraph(self.theme.replace_bold_with_font(section), self.style(self.paragraph_styles.SUB_LIST)) for section in sections]

        elements += ListElement(sections, bulletType='bullet', bulletColor=self.theme.colors.get("light_blue"), leftIndent=-0.5 * cm).render()
        elements += PageBreak()

        return elements

    def add_cover(self):
        today = self._format_date(datetime.now())
        start, end = map(self._format_date, self.config.date_range)
        client_name, client_logo = self.config.client_details

        text = self._prepare_text(today, start, end, client_name)
        footer = f"© {datetime.now().year} Soluciones Netready, C.A. All Rights Reserved."

        return Cover(self.metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, self.theme).render()

    def run(self):
        self.elements += self.add_cover()
        self.elements += self.add_introduction()

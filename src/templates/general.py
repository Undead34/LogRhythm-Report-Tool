import pandas as pd
from src.utils import ElementList
from .canvas import Canvas
from typing import TYPE_CHECKING
from datetime import datetime
from reportlab.lib.units import cm
from src.themes import theme
from src.components import Bar, Cover, Line, PageBreak, Paragraph, Table, ListElement, Spacer

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
        self.font_names = theme.FontsNames

    def add_cover(self):
        today = self._format_date(datetime.now())
        start, end = map(self._format_date, self.config.date_range)
        client_name, client_logo = self.config.client_details

        text = self._prepare_text(today, start, end, client_name)
        footer = f"© {datetime.now().year} Soluciones Netready, C.A. All Rights Reserved."

        return Cover(self.metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, self.theme).render()

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

        elements += ListElement(sections, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='bullet', bulletColor=self.theme.colors.get("light_blue"), leftIndent=-0.5 * cm).render()
        elements += PageBreak()

        return elements

    def add_alarm_trends_with_description(self):
        elements = ElementList()

        elements += Paragraph("Tendencias de Alarmas por Prioridad", self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph(
            self.theme.replace_bold_with_font(
                """
                El gráfico de tendencias de alarmas por prioridad ofrece una representación visual detallada de la evolución y distribución temporal de las alarmas registradas en el sistema de monitoreo LogRhythm. Este gráfico se basa en datos agrupados y procesados para mostrar claramente cómo varían las ocurrencias de diferentes alarmas a lo largo del tiempo, separando las alarmas de baja prioridad en una categoría **'Low Priority'** para una mayor claridad visual.
                """
            ),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        elements += Paragraph("Cómo Leer el Gráfico:", self.style(self.paragraph_styles.TITLE_2))

        components_items = [
            "**Eje X (Horizontal)**: Representa las fechas. Cada punto en el eje X corresponde a un día específico.",
            "**Eje Y (Vertical)**: Representa el número de activaciones. Este eje muestra la cantidad de veces que cada alarma fue activada en un día dado.",
            "**Líneas de Tendencia**: Cada línea en el gráfico corresponde a una alarma específica. Las líneas de diferentes colores permiten distinguir entre las diferentes alarmas.",
            "**Leyenda**: Identifica cada alarma por su nombre. La leyenda facilita la comprensión de qué línea corresponde a cada alarma.",
            "**Anotaciones de Máximos**: Los puntos donde una alarma alcanza su máxima cantidad de activaciones en un día específico están anotados con etiquetas que indican el valor máximo de activaciones y la fecha en que ocurrió.",
            "**Líneas Verticales y Anotaciones de Eventos Únicos**: Si una alarma se activó solo una vez en un día específico, se añade una línea vertical discontinua y una anotación en ese punto para destacar este evento.",
            "**Total de Eventos**: En la esquina inferior derecha del gráfico, se muestra el número total de activaciones de todas las alarmas representadas en el gráfico."
        ]
        components_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in components_items]
        elements += ListElement(components_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        elements += Paragraph("Interpretación del Gráfico:", self.style(self.paragraph_styles.TITLE_2))

        interpretation_items = [
            "**Identificación de Picos y Tendencias**: Los picos en las líneas de tendencia permiten identificar días con un alto número de activaciones para ciertas alarmas.",
            "**Comparación de Alarmas**: Las diferentes alarmas pueden ser comparadas para determinar cuáles son las más frecuentes o cuáles presentan picos de alta activación.",
            "**Análisis Temporal**: Las activaciones de alarmas pueden ser analizadas a lo largo del tiempo para identificar patrones de cambio.",
            "**Eventos Únicos**: Las anotaciones de eventos únicos permiten identificar eventos raros o críticos.",
            "**Prioridad de Alarmas**: Las alarmas de baja prioridad se presentan separadamente para mantener la claridad del gráfico y enfocar la atención en las alarmas de mayor importancia."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        # Gráfico completo
        full_figure = self.alarm_activation_line_graph(chunk=True)
        elements += full_figure
        full_description = Paragraph(
            self.theme.replace_bold_with_font(
                """
                El gráfico completo presenta una visión integral de todas las alarmas activadas en el período del informe, permitiendo observar la tendencia general de la actividad de alarmas en el sistema a lo largo del tiempo.
                """
            ),
            self.style(self.paragraph_styles.TEXT_GRAPHIC)
        )
        full_description.hAlign = 'CENTER'
        elements += full_description

        # Gráficos segmentados por prioridad
        chunk_figures = self.alarm_activation_line_graph(chunk=False)
        for idx, figure in enumerate(chunk_figures, start=1):
            elements += figure
            chunk_description = Paragraph(
                self.theme.replace_bold_with_font(
                    f"""
                    El gráfico a continuación muestra las tendencias específicas de las alarmas de prioridad {idx}, proporcionando un análisis detallado y enfocado que facilita la identificación de patrones y comportamientos particulares en las alarmas de esta categoría.
                    """
                ),
                self.style(self.paragraph_styles.TEXT_GRAPHIC)
            )
            chunk_description.hAlign = 'CENTER'
            elements += chunk_description

        return elements


    def run(self):
        self.elements += self.add_cover()
        self.elements += self.add_introduction()


        self.elements += Paragraph(self.theme.replace_bold_with_font("Indicadores de cumplimiento de SLA y Tiempos de Gestión").upper(), self.style(self.paragraph_styles.TITLE_1))

        self.elements += Spacer(0, 0.5 * cm)

        self.elements += self.add_alarm_trends_with_description()

    def alarm_activation_line_graph(self, chunk: bool = False):
        df = self._process_alarm_data()

        if chunk:
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
                title='Distribución de Alarmas y Prioridad a lo Largo del Tiempo',
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

    # Private
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

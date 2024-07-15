import pandas as pd
from src.utils import ElementList
from .canvas import Canvas
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from reportlab.lib.units import cm
from src.themes import theme
from src.components import Bar, Cover, Line, PageBreak, Paragraph, Table, ListElement, Historigram, Spacer
import calendar

if TYPE_CHECKING:
    from src.databases import MSQLServer, Package
    from src.app import Config
    from src.reports.skeleton import Report

class GeneralTemplate:
    canvasmaker: Canvas
    elements: ElementList

    def __init__(self, report: 'Report', queries: 'list[Package]', database: 'MSQLServer', metadata: dict, config: 'Config') -> None:
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
        footer = f"© {datetime.now().year} Soluciones Netready, C.A. Todos los Derechos Reservados."

        return Cover(self.metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, self.theme).render()

    def add_introduction(self):
        elements = ElementList()
        elements += Paragraph("Introducción".upper(), self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph("1. Objetivo del Informe", self.style(self.paragraph_styles.TITLE_2))

        intro_text = """
            **Propósito**: Proporcionar una visión detallada y automatizada del estado del Sistema de Gestión de Información y Eventos de Seguridad (SIEM), destacando los aspectos clave relacionados con la seguridad, el rendimiento y la conformidad.
            
            **Alcance**: Este informe cubre la actividad del SIEM durante el periodo especificado, incluyendo la identificación de atacantes, vulnerabilidades, alarmas, violaciones de cumplimiento, fallas operativas, violaciones de auditoría, detalles de logs, estadísticas de componentes y resúmenes automáticos.
            
            **Metodología**: Los datos presentados han sido recopilados y analizados utilizando herramientas automatizadas que integran y correlacionan información de múltiples fuentes. Los gráficos y tablas incluidos son el resultado de análisis estadísticos diseñados para resaltar tendencias significativas y puntos críticos.
            
            **Estructura del Informe**: El informe se divide en varias secciones clave:
        """
        elements += Paragraph(self.theme.replace_bold_with_font(intro_text), self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

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

    def add_ttd_ttr_by_month_table_with_description(self):
        elements = ElementList()

        elements += Paragraph("Indicadores de Tiempos de Detección y Respuesta por Mes", self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph(
            self.theme.replace_bold_with_font(
                "Los tiempos de detección (TTD) y respuesta (TTR) son métricas críticas para evaluar la eficiencia y efectividad del sistema de monitoreo de seguridad. La siguiente tabla proporciona un desglose de estos indicadores por mes, permitiendo identificar áreas de mejora y resaltar buenas prácticas."
            ),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        elements += Paragraph("Cómo Interpretar la Tabla:", self.style(self.paragraph_styles.TITLE_2))

        interpretation_items = [
            "**Mes**: El mes en el que se registraron los eventos.",
            "**Nº de alarmas**: La cantidad total de alarmas registradas en cada mes.",
            "**TTD Promedio**: El tiempo promedio que tomó detectar un evento desde su ocurrencia.",
            "**TTD Máximo**: El tiempo máximo registrado para la detección de un evento.",
            "**TTR Promedio**: El tiempo promedio que tomó responder a un evento una vez detectado.",
            "**TTR Máximo**: El tiempo máximo registrado para responder a un evento."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()
        
        elements += Spacer(0, 1 * cm)

        # Obtener y procesar los datos
        df = self.db.get_alarms_information()
        df['GeneratedOn'] = pd.to_datetime(df['GeneratedOn']).dt.tz_localize(None)  # Eliminar la información de la zona horaria
        df['Month'] = df['GeneratedOn'].dt.to_period('M')

        # Filtrar valores negativos y NaN
        df = df.dropna(subset=['TTD', 'TTR'])
        df = df[(df['TTD'] >= 0) & (df['TTR'] >= 0)]

        # Agrupar y calcular los promedios y máximos por mes
        monthly_data = df.groupby('Month').agg(
            Alarms=('AlarmID', 'count'),
            Avg_TTD=('TTD', 'mean'),
            Max_TTD=('TTD', 'max'),
            Avg_TTR=('TTR', 'mean'),
            Max_TTR=('TTR', 'max')
        ).reset_index()

        # Formatear tiempos en HH:MM:SS
        def format_timedelta(seconds):
            return str(timedelta(seconds=int(seconds))) if pd.notnull(seconds) else '00:00:00'

        for col in ['Avg_TTD', 'Max_TTD', 'Avg_TTR', 'Max_TTR']:
            monthly_data[col] = monthly_data[col].apply(format_timedelta)

        # Traducir los nombres de los meses al español
        monthly_data['Month'] = monthly_data['Month'].apply(lambda x: calendar.month_name[x.month].capitalize())
        monthly_data['Month'] = monthly_data['Month'].replace({
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril', 
            'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto', 
            'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        })

        column_names = ['Mes', 'Nº de alarmas', 'TTD Promedio', 'TTD Máximo', 'TTR Promedio', 'TTR Máximo']

        elements += Table(monthly_data, self.style(self.tables_styles.DEFAULT), column_names, mode='fit-full').render()

        return elements

    def add_ttd_ttr_by_msgclassname_table_with_description(self):
        elements = ElementList()

        elements += Paragraph("Indicadores de Tiempos de Detección y Respuesta por Clasificación", self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph(
            self.theme.replace_bold_with_font(
                "Los tiempos de detección (TTD) y respuesta (TTR) son métricas críticas para evaluar la eficiencia y efectividad del sistema de monitoreo de seguridad. La siguiente tabla proporciona un desglose de estos indicadores por cada clasificación de mensaje, permitiendo identificar áreas de mejora y resaltar buenas prácticas."
            ),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        elements += Paragraph("Cómo Interpretar la Tabla:", self.style(self.paragraph_styles.TITLE_2))

        interpretation_items = [
            "**Clasificación**: El tipo de mensaje o evento capturado por el SIEM.",
            "**Nº de alarmas**: La cantidad total de alarmas registradas para cada clasificación.",
            "**TTD Promedio**: El tiempo promedio que tomó detectar un evento desde su ocurrencia.",
            "**TTD Máximo**: El tiempo máximo registrado para la detección de un evento.",
            "**TTR Promedio**: El tiempo promedio que tomó responder a un evento una vez detectado.",
            "**TTR Máximo**: El tiempo máximo registrado para responder a un evento."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        elements += Spacer(0, 1 * cm)

        # Agregar la tabla de TTD y TTR por clasificación de mensaje
        df = self.db.get_TTD_AND_TTR_by_msg_class_name()

        # Formatear tiempos en HH:MM:SS
        for col in ['Avg_TTD', 'Max_TTD', 'Avg_TTR', 'Max_TTR']:
            df[col] = df[col].apply(lambda x: str(timedelta(seconds=int(x))) if pd.notnull(x) else '00:00:00')

        column_names = ['Clasificación', 'Nº de alarmas', 'TTD Promedio', 'TTD Máximo', 'TTR Promedio', 'TTR Máximo']

        elements += Table(df, self.style(self.tables_styles.DEFAULT), column_names, mode='fit-full').render()

        return elements

    def add_alarm_trends_with_description(self):
        elements = ElementList()

        elements += Paragraph("Tendencias de Alarmas por Prioridad", self.style(self.paragraph_styles.TITLE_1))
        description = """
            El gráfico de tendencias de alarmas por prioridad ofrece una representación visual detallada de la evolución y distribución temporal de las alarmas registradas en el sistema de monitoreo LogRhythm. Este gráfico se basa en datos agrupados y procesados para mostrar claramente cómo varían las ocurrencias de diferentes alarmas a lo largo del tiempo, separando las alarmas de baja prioridad en una categoría **'Low Priority'** para una mayor claridad visual.
        """
        elements += Paragraph(self.theme.replace_bold_with_font(description), self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

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
        full_figure = self._alarm_activation_line_graph(chunk=True)
        elements += full_figure
        full_description = Paragraph(
            self.theme.replace_bold_with_font(
                "El gráfico completo presenta una visión integral de todas las alarmas activadas en el período del informe."
            ),
            self.style(self.paragraph_styles.TEXT_GRAPHIC)
        )
        full_description.hAlign = 'CENTER'
        elements += full_description

        # Gráficos segmentados por prioridad
        chunk_figures = self._alarm_activation_line_graph(chunk=False)
        for idx, figure in enumerate(chunk_figures, start=1):
            elements += figure
            chunk_description = Paragraph(
                self.theme.replace_bold_with_font(
                    f"Gráfico Segmentado {idx}: Este gráfico proporciona un análisis detallado de un subconjunto específico de alarmas."
                ),
                self.style(self.paragraph_styles.TEXT_GRAPHIC)
            )
            chunk_description.hAlign = 'CENTER'
            elements += chunk_description

        return elements

    def add_event_distribution(self):
        # Obtener los datos de la consulta
        df = next(q.run() for q in self.queries if q._id == "34607e55-49ea-44d9-a152-b3d2bdbae24b")
        df['date'] = pd.to_datetime(df['date'])
        
        elements = ElementList()

        # Título
        elements += Paragraph("Distribución de Eventos por Hora y por Día", self.style(self.paragraph_styles.TITLE_1))

        # Descripción del gráfico
        elements += Paragraph(
            self.theme.replace_bold_with_font(
                "Los siguientes gráficos muestran la distribución de eventos registrados. El primer gráfico muestra la cantidad de eventos por hora a lo largo del período analizado, mientras que el segundo gráfico muestra la cantidad de eventos por día. Estos análisis permiten identificar patrones temporales tanto diarios como horarios en la ocurrencia de eventos."
            ),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        # Cómo leer los gráficos
        elements += Paragraph("Cómo Leer los Gráficos:", self.style(self.paragraph_styles.TITLE_2))

        interpretation_items = [
            "**Eje X (Horizontal)**: En el primer gráfico, representa las horas del día, desde las 00:00 hasta las 23:00. En el segundo gráfico, representa los días del mes.",
            "**Eje Y (Vertical)**: Representa el número total de eventos registrados.",
            "**Barras**: La altura de cada barra indica la cantidad de eventos ocurridos en esa hora (primer gráfico) o en ese día (segundo gráfico)."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        # Crear el histograma por hora
        elements += Historigram(df, "date", 'count', show_legend=False, freq="1h", title="Distribución de Eventos por Hora").plot()
        # Crear el histograma por día
        elements += Historigram(df, "date", 'count', show_legend=False, freq="1D", title="Distribución de Eventos por Día").plot()

        return elements
    
    def add_top_alarms(self):
        elements = ElementList()
        elements += Paragraph("Top Alarmas", self.style(self.paragraph_styles.TITLE_1))
        elements += Paragraph(
            self.theme.replace_bold_with_font(
                "El siguiente gráfico muestra el top 10 alarmas registradas, ordenadas por la cantidad de veces que se activaron."
            ),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        df = self.db.get_alarms_information()
        df = df.groupby('AlarmRuleName', observed=False).size().reset_index(name='Count')
        df = df.sort_values(by='Count', ascending=False)

        bar = Bar(df.head(10), x_col='AlarmRuleName', y_col='Count', show_xticks=False, show_legend=True)
        elements += bar.plot()

        return elements

    def run(self):
        self.elements += self.add_cover()
        self.elements += self.add_introduction()

        self.elements += Paragraph(self.theme.replace_bold_with_font("Indicadores de cumplimiento de SLA y Tiempos de Gestión").upper(), self.style(self.paragraph_styles.TITLE_1))
        self.elements += self.add_ttd_ttr_by_month_table_with_description()
        self.elements += self.add_ttd_ttr_by_msgclassname_table_with_description()
        self.elements += self.add_alarm_trends_with_description()
        self.elements += self.add_event_distribution()
        self.elements += self.add_top_alarms()

        df = next(q.run() for q in self.queries if q._id == "337fb1d3-a5be-4f20-9928-f662ae002910")
        chart = Bar(df, x_col='key', y_col='doc_count', title='Distribución de Eventos por Categoría', orientation='horizontal', show_legend=False, axis_labels=True)
        self.elements += chart.plot()



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

    def _alarm_activation_line_graph(self, chunk: bool = False):
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

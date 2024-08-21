# Standard library imports
import calendar
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import json
import threading
import time

# Third-party library imports
import pandas as pd
from reportlab.lib.units import cm
from babel.numbers import format_number
from reportlab.platypus import Paragraph, Spacer, PageBreak
from tqdm import tqdm

# Local application imports
from src.utils import ElementList, logger
from src.themes import theme
from src.components import Table, KPI, Bar, ListElement, Historigram, Line
from .utils import get_human_readable_period
from .canvas import Canvas
from .first_pages import introduction, cover

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
        self.logger = logger.get_logger()
        self.stop_compiling = threading.Event()  # Evento para detener la barra de progreso infinita
        self.progress_thread = None  # Referencia al hilo de la barra de progreso

    def run(self):
        steps = 10  # Total de pasos (ajusta según tus secciones)
        
        with tqdm(total=steps, desc="Generando reporte", unit="paso") as pbar:
            self.logger.debug("Añadiendo portada e introducción al informe")
            self.elements += cover(self.config, self.metadata, self.theme)
            self.elements += introduction(self.theme)
            pbar.update(1)  # Actualiza la barra de progreso

            self.elements += self.add_state_of_siem()
            pbar.update(1)

            self.elements += self.add_threat_analysis()
            pbar.update(1)

            self.elements += Paragraph("2. Análisis de Eventos", self.style(self.paragraph_styles.TITLE_2))
            pbar.update(1)

            self.elements += self.add_event_distribution()
            pbar.update(1)

            self.elements += self.add_event_distribution_by_priority()
            pbar.update(1)

            self.elements += self.add_event_distribution_by_class()
            pbar.update(1)

            self.elements += Paragraph("3. Análisis de Alarmas", self.style(self.paragraph_styles.TITLE_2))

            pbar.update(1)
            self.elements += self.add_alarm_status_table()

            pbar.update(1)
            self.elements += self.add_alarm_trends_with_description()

            pbar.update(1)
            self.elements += self.add_classification_name_count_table()

        self.progress_thread = threading.Thread(target=self.compiling_progress_bar)
        self.progress_thread.start()

    def compiling_progress_bar(self):
        with tqdm(desc="Compilando...", bar_format="{l_bar}{bar} [Tiempo transcurrido: {elapsed}]") as pbar:
            while not self.stop_compiling.is_set():
                pbar.update(1)
                time.sleep(0.1)  # Intervalo de actualización

    def add_state_of_siem(self):
        elements = ElementList()
        elements += Paragraph("Estado General del SIEM", self.style(self.paragraph_styles.SUB_TITLE_1))
        
        (start_date, end_date) = self.config.date_range
        (start_date, end_date) = get_human_readable_period(start_date, end_date)
        
        # Obtención de la agregación por tipo de fuente
        events = next(q.run() for q in self.queries if q._id == "agg_logs_by_source_type")
        alarms_count = format_number(self.db.get_alarm_count(), "es_ES")
        events_count = format_number(next(q.run() for q in self.queries if q._id == "count_events")["total"][0], "es_ES")
        logs_count = format_number(next(q.run() for q in self.queries if q._id == "count_non_event_logs")["total"][0], "es_ES")

        # Introducción del Estado General del SIEM
        intro_text = f"""
        Este es el estado general del Sistema de Información y Monitoreo (SIEM) para el periodo comprendido 
        entre {start_date} y {end_date}. Durante este periodo, hemos recopilado y procesado una gran cantidad de logs, 
        diferenciando entre eventos de seguridad y otros tipos de logs relacionados. A continuación, se proporciona una visión detallada de cómo se distribuyen los eventos según su tipo de fuente.
        """
        elements += Paragraph(intro_text, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        # Preparación de los datos para la tabla
        data = []

        for _, row in events.iterrows():
            source_type = row["key"]
            count = row["doc_count"]
            data.append([f"Logs de {source_type}", format_number(count, locale='es')])

        # Crear y añadir la tabla
        df = pd.DataFrame(columns=["Descripción", "Valor"], data=data)

        table_style = self.style(self.tables_styles.DEFAULT)
        table = Table(df, style=table_style, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm)
        elements += Spacer(0, 0.5 * cm)
        elements += table.render()
        elements += Spacer(0, 0.5 * cm)

        # Explicación sobre los eventos versus logs
        explanation_text = f"""
        Durante el periodo analizado, el SIEM ha gestionado una diversidad de fuentes de logs, 
        desde dispositivos de red como Fortinet Fortigate y Trend Micro, hasta sistemas operativos 
        y aplicaciones. La clasificación de estos logs es crucial para entender la naturaleza de los eventos 
        que podrían requerir atención inmediata.
        """
        elements += Paragraph(explanation_text, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))
        
        # Asegúrate de convertir la columna 'doc_count' a enteros si es posible
        events["doc_count"] = pd.to_numeric(events["doc_count"], errors='coerce').fillna(0).astype(int)
        
        # Crear gráfico de barras
        elements += Bar(events, "key", y_col="doc_count", axis_labels=True, xlabel="Tipo de Fuente de Log", ylabel="Cantidad", xtick_rotation=90).plot()

        elements += PageBreak()

        return elements

    def add_threat_analysis(self):
        style = self.style(self.paragraph_styles.SUB_TITLE_1)
        elements = ElementList()
        elements += Paragraph("Análisis de Amenazas", style)
        
        elements += Paragraph("Durante el período del informe, se detectaron varios tipos de amenazas. La siguiente tabla muestra la distribución del número de eventos de amenazas por tipo y su frecuencia relativa.", self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        # Obtención de datos de la base de datos
        data = next(q.run() for q in self.queries if q._id == "classification_name_count")

        # Helper function to safely extract data
        def get_frequency(key):
            if key in data["key"].values:
                return data[data["key"] == key]["doc_count"].values[0]
            else:
                return 0

        # Filtrar las amenazas relevantes
        threat_data = [
            {"Threat Type": "Malware", "Frequency": get_frequency("malware")},
            {"Threat Type": "Acceso Fallido", "Frequency": get_frequency("access failure")},
            {"Threat Type": "Fallo de Autenticación", "Frequency": get_frequency("authentication failure")},
            {"Threat Type": "Actividad Sospechosa", "Frequency": get_frequency("suspicious")},
            {"Threat Type": "Vulnerabilidad", "Frequency": get_frequency("vulnerability")},
            {"Threat Type": "Ataque", "Frequency": get_frequency("attack")},
        ]

        # Convertir los datos a DataFrame
        threat_df = pd.DataFrame(threat_data)

        # Calcular el porcentaje de cada amenaza
        total_threats = threat_df["Frequency"].sum()
        if total_threats > 0:
            threat_df["Frequency (%)"] = threat_df["Frequency"] / total_threats * 100
        else:
            threat_df["Frequency (%)"] = 0

        # Ordenar los datos por "Frequency (%)" antes de formatear
        threat_df = threat_df.sort_values(by="Frequency (%)", ascending=False)

        # Formatear los datos
        threat_df["Frequency"] = threat_df["Frequency"].apply(lambda x: format_number(x, locale='es'))
        threat_df["Frequency (%)"] = threat_df["Frequency (%)"].apply(lambda x: f"{x:.2f}%")

        # Crear la tabla con los datos
        table_style = self.style(self.tables_styles.DEFAULT)
        elements += Table(threat_df, style=table_style, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm).render()
        elements += Spacer(1, 12)

        elements += PageBreak()

        return elements

    def add_event_distribution(self):
        elements = ElementList()

        # Descripción del gráfico
        description_text = (
            "El siguiente gráfico muestra la distribución de eventos registrados por día. "
            "Este análisis permite identificar patrones temporales en la ocurrencia diaria de eventos."
        )
        elements += Paragraph(
            description_text,
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        # Obtener los datos de la consulta
        df = next(q.run() for q in self.queries if q._id == "events_histogram")

        if df.empty:
            return []

        df["key_as_string"] = pd.to_datetime(df["key_as_string"])

        # Crear el histograma por día
        elements += Historigram(df, "key_as_string", "doc_count", show_legend=False, freq="1D", title="Distribución de Eventos por Día", xlabel="Días del mes", ylabel="Eventos por día").plot()
        
        elements += Paragraph("Distribución de Eventos por Día", self.style(self.paragraph_styles.TEXT_GRAPHIC))
        elements += Paragraph("Cómo Interpretar el Gráfico:", self.style(self.paragraph_styles.SUB_TITLE_1))

        interpretation_items = [
            "**Eje X (Horizontal)**: Representa los días del mes.",
            "**Eje Y (Vertical)**: Representa el número total de eventos registrados.",
            "**Barras**: La altura de cada barra indica la cantidad de eventos ocurridos en ese día."
        ]
        interpretation_paragraphs = [Paragraph(item, self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        elements += Spacer(0, 1 * cm)

        return elements

    def add_event_distribution_by_priority(self):
        elements = ElementList()

        # Descripción del gráfico
        description_text = (
            "El siguiente gráfico muestra la distribución de eventos registrados por día, "
            "según la prioridad de los eventos. Este análisis permite identificar patrones temporales "
            "diarios en la ocurrencia de eventos para cada categoría de prioridad."
        )
        elements += Paragraph(
            description_text,
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        # Obtener los datos de la consulta
        df = next(q.run() for q in self.queries if q._id == "events_histogram_by_priority")
        
        if df.empty:
            return []
        
        df["key_as_string"] = pd.to_datetime(df["key_as_string"])

        def categorize_priority(priority):
            if priority <= 50:
                return 'Prioridad Baja'
            elif priority <= 75:
                return 'Prioridad Media'
            else:
                return 'Prioridad Alta'
        
        df['priority_category'] = df['key'].apply(categorize_priority)

        # Ordenar el DataFrame por fecha
        df = df.sort_values(by="key_as_string")

        # Separar el DataFrame en múltiples DataFrames según la categoría de prioridad
        dataframes = {priority: group for priority, group in df.groupby('priority_category')}

        ordered_priorities = ['Prioridad Baja', 'Prioridad Media', 'Prioridad Alta']

        for priority_category in ordered_priorities:
            if priority_category in dataframes:
                df_group = dataframes[priority_category]
                # Crear el histograma por día para cada categoría de prioridad
                elements += Historigram(
                    df_group, "key_as_string", "doc_count", show_legend=False, freq="1D",
                    title=f"Distribución de Eventos por Día - {priority_category.capitalize()}", 
                    xlabel="Días del mes", ylabel="Eventos por día"
                ).plot()

                elements += Paragraph(f"Distribución de Eventos por Día - {priority_category.capitalize()}", self.style(self.paragraph_styles.TEXT_GRAPHIC))
                elements += Paragraph("Cómo Interpretar el Gráfico:", self.style(self.paragraph_styles.SUB_TITLE_1))

                interpretation_items = [
                    "**Eje X (Horizontal)**: Representa los días del mes.",
                    "**Eje Y (Vertical)**: Representa el número total de eventos registrados.",
                    "**Barras**: La altura de cada barra indica la cantidad de eventos ocurridos en ese día."
                ]
                interpretation_paragraphs = [Paragraph(item, self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
                elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

                elements += Spacer(0, 1 * cm)

        return elements

    def add_event_distribution_by_class(self):
        elements = ElementList()

        # Descripción del gráfico
        description_text = (
            "El siguiente gráfico muestra la distribución de eventos registrados por día, "
            "según la clase de mensaje. Este análisis permite identificar patrones temporales "
            "diarios en la ocurrencia de eventos para cada clase de mensaje."
        )
        elements += Paragraph(
            description_text,
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )

        # Obtener los datos de la consulta
        df = next(q.run() for q in self.queries if q._id == "events_histogram_by_msgclassname")
        if df.empty:
            return []
        
        df["key_as_string"] = pd.to_datetime(df["key_as_string"])

        dataframes = {msg_class_name: group for msg_class_name, group in df.groupby('key')}

        for msg_class_name, df_group in dataframes.items():
            # Crear el histograma por día para cada clase de mensaje
            elements += Historigram(
                df_group, "key_as_string", "doc_count", show_legend=False, freq="1D",
                title=f"Distribución de Eventos por Día - {msg_class_name.capitalize()}", 
                xlabel="Días del mes", ylabel="Eventos por día"
            ).plot()

            elements += Paragraph(f"Distribución de Eventos por Día - {msg_class_name.capitalize()}", self.style(self.paragraph_styles.TEXT_GRAPHIC))
        
        elements += Paragraph("Cómo Interpretar los Gráficos:", self.style(self.paragraph_styles.SUB_TITLE_1))

        interpretation_items = [
            "**Eje X (Horizontal)**: Representa los días del mes.",
            "**Eje Y (Vertical)**: Representa el número total de eventos registrados.",
            "**Barras**: La altura de cada barra indica la cantidad de eventos ocurridos en ese día."
        ]
        interpretation_paragraphs = [Paragraph(item, self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

        elements += Spacer(0, 1 * cm)

        return elements

    def add_alarm_status_table(self):
        elements = ElementList()

        # Obtener y procesar los datos
        df = self.db.get_alarms_information()
        
        if df.empty:
            return []
        
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate'])

        # Obtener entidades y mapear EntityID a Name
        entities_df = self.db.get_entities()
        entity_dict = dict(zip(entities_df['EntityID'], entities_df['Name']))
        df['EntityName'] = df['EntityID'].map(entity_dict)

        # Excluir las alarmas con estado "New", "OpenAlarm", "Working" y "Monitor"
        initial_count = df.shape[0]
        df_filtered = df[~df['AlarmStatus'].isin(['New', 'OpenAlarm', 'Working', 'Monitor'])]
        final_count = df_filtered.shape[0]
        total_removed = initial_count - final_count

        elements += Paragraph(self.theme.replace_bold_with_font(f"""
            Esta tabla proporciona un resumen del número de alarmas en LogRhythm que se han clasificado en diferentes estados.
            Se excluyen las alarmas en estado **Nueva**, **Alarma Abierta**, **Trabajando** y **Monitorear** para enfocarse en aquellos estados que indican una resolución específica.
            La información presentada en esta tabla ayuda a los usuarios a tener una visión clara de la distribución de las alarmas según su estado."""), self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        elements += Paragraph(self.theme.replace_bold_with_font(f"""
            De un total inicial de {format_number(initial_count, locale='es_ES')} alarmas, se excluyeron {format_number(total_removed, locale='es_ES')} registros con estado **Nueva**, **Alarma Abierta**, **Trabajando** o **Monitorear**, resultando en {format_number(final_count, locale='es_ES')} alarmas consideradas para el análisis.
        """), self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        # Agrupar los datos por 'EntityName', 'AlarmRuleName' y 'AlarmStatus'
        alarms = df_filtered.groupby(['EntityName', 'AlarmRuleName', 'AlarmStatus']).size().unstack(fill_value=0).reset_index()

        # Formatear los números en el DataFrame usando Babel
        for col in alarms.columns[2:]:
            alarms[col] = alarms[col].apply(lambda x: format_number(x, locale='es_ES'))

        # Crear la tabla de datos
        column_names = ['Entidad', 'Nombre de Alarma'] + [col for col in alarms.columns if col not in ['EntityName', 'AlarmRuleName', 'AlarmStatus']]
        table_style = self.style(self.tables_styles.DEFAULT)
        table = Table(alarms, table_style, column_names, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm).render()
        
        elements += table

        # Añadir el título y la descripción de la tabla
        elements += Paragraph("Tabla de Conteo de Estados de Alarma en LogRhythm", self.style(self.paragraph_styles.TEXT_GRAPHIC))

        elements += Spacer(0, 1 * cm)

        return elements

    def add_alarm_trends_with_description(self):
        elements = ElementList()

        elements += Paragraph(self.theme.replace_bold_with_font(
            """
            El gráfico de tendencias de alarmas por prioridad ofrece una representación visual detallada de la evolución y distribución temporal de las alarmas registradas en el sistema de monitoreo LogRhythm. Este gráfico se basa en datos agrupados y procesados para mostrar claramente cómo varían las ocurrencias de diferentes alarmas a lo largo del tiempo, separando las alarmas de baja prioridad en una categoría **'Low Priority'** para una mayor claridad visual.
            """
        ), self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        elements += Paragraph("Cómo Leer el Gráfico:", self.style(self.paragraph_styles.SUB_TITLE_1))

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

        # Gráfico completo
        full_figure = self._alarm_activation_line_graph(chunk=True)

        if len(full_figure) == 0:
            return []

        elements += full_figure
        full_description = Paragraph(
            self.theme.replace_bold_with_font(
                "El gráfico completo presenta una visión integral de todas las alarmas activadas en el período del informe."
            ),
            self.style(self.paragraph_styles.TEXT_GRAPHIC)
        )
        full_description.hAlign = 'CENTER'
        elements += full_description

        elements += Paragraph("Interpretación del Gráfico:", self.style(self.paragraph_styles.SUB_TITLE_1))

        interpretation_items = [
            "**Identificación de Picos y Tendencias**: Los picos en las líneas de tendencia permiten identificar días con un alto número de activaciones para ciertas alarmas.",
            "**Comparación de Alarmas**: Las diferentes alarmas pueden ser comparadas para determinar cuáles son las más frecuentes o cuáles presentan picos de alta activación.",
            "**Análisis Temporal**: Las activaciones de alarmas pueden ser analizadas a lo largo del tiempo para identificar patrones de cambio.",
            "**Eventos Únicos**: Las anotaciones de eventos únicos permiten identificar eventos raros o críticos.",
            "**Prioridad de Alarmas**: Las alarmas de baja prioridad se presentan separadamente para mantener la claridad del gráfico y enfocar la atención en las alarmas de mayor importancia."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()

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

    def _alarm_activation_line_graph(self, chunk: bool = False):
        df = self.db.get_alarms_information()
        
        if df.empty:
            return []
        
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')
        df = df.groupby(['AlarmDate', 'AlarmRuleName', 'AlarmPriority'], observed=False).size().reset_index(name='Counts')

        priority = 50
        low_priority = df[df['AlarmPriority'] < priority].groupby('AlarmDate', observed=False)['Counts'].sum().reset_index()
        low_priority['AlarmRuleName'] = 'Low Priority'

        df = df[df['AlarmPriority'] >= priority]
        df = pd.concat([df, low_priority], ignore_index=True)

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


    def add_classification_name_count_table(self):
        elements = ElementList()

        elements += Paragraph("Distribución de Eventos por Clasificación", self.style(self.paragraph_styles.TITLE_2))

        # Descripción de la tabla
        description_text = (
            "La tabla siguiente muestra la distribución de eventos registrados según su clasificación. "
            "Este análisis permite identificar cuáles son los tipos de eventos más frecuentes y ayuda en la priorización de acciones de respuesta."
        )
        elements += Paragraph(
            self.theme.replace_bold_with_font(description_text),
            self.style(self.paragraph_styles.SUB_TEXT_NORMAL)
        )
        
        # Procesar y formatear los datos
        column_names = ['Clasificación', 'Cantidad']
        table_style = self.style(self.tables_styles.DEFAULT)
        
        df = next(q.run() for q in self.queries if q._id == "8b47b29f-0dae-4f07-ace0-de0d138ef8ae")
        df['doc_count'] = pd.to_numeric(df['doc_count'], errors='coerce')
        df['doc_count'] = df['doc_count'].apply(lambda x: format_number(x, locale='es_ES') if pd.notnull(x) else 'N/A')

        # Crear una tabla para mostrar los datos
        table = Table(df, table_style, column_names, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm).render()
        elements += table
        
        elements += Paragraph("Distribución de eventos por clasificación.", self.style(self.paragraph_styles.TEXT_GRAPHIC))
        
        elements += Paragraph("Cómo Interpretar la Tabla:", self.style(self.paragraph_styles.SUB_TITLE_1))
        interpretation_items = [
            "**Clasificación**: El tipo de evento registrado.",
            "**Cantidad**: El número total de eventos registrados para cada clasificación."
        ]
        interpretation_paragraphs = [Paragraph(self.theme.replace_bold_with_font(item), self.style(self.paragraph_styles.SUB_LIST)) for item in interpretation_items]
        elements += ListElement(interpretation_paragraphs, bulletFontName=self.font_names.ARIALNARROW.value, bulletType='1', bulletFormat='%s.', leftIndent=-0.5 * cm).render()
        
        elements += Spacer(0, 1 * cm)
        
        return elements

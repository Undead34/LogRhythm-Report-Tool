# Standard library imports
import calendar
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import json

# Third-party library imports
import pandas as pd
from reportlab.lib.units import cm
from babel.numbers import format_number
from reportlab.platypus import Paragraph, Spacer, PageBreak

# Local application imports
from src.utils import ElementList, logger
from src.themes import theme
from src.components import Table, ComparisonLine, KPI
from .utils import get_human_readable_period, aux_parse_12
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

    def run(self):
        self.logger.debug("Añadiendo portada al informe e introducción")
        
        self.elements += cover(self.config, self.metadata, self.theme)
        self.elements += introduction(self.theme)
        # self.elements += self.add_state_of_siem()

        # self.elements += self.add_threat_analysis()
        # self.elements += self.add_incident_response()
        # self.elements += self.add_trends_and_comparatives()
        # self.elements += self.add_recommendations()
        # self.elements += self.add_conclusion()
        
        # MS Windows Event Logging XML - Application
        # MS Windows Event Logging XML - Security
        # MS Windows Event Logging XML - System

    def add_state_of_siem(self):
        elements = ElementList()
        elements += Paragraph("Estado General del SIEM", self.style(self.paragraph_styles.SUB_TITLE_1))
        
        (start_date, end_date) = self.config.date_range
        (start_date, end_date) = get_human_readable_period(start_date, end_date)

        # Introducción del Estado General del SIEM
        intro_text = f"""
        Este es el estado general del Sistema de Información y Monitoreo (SIEM). 
        Proporciona una visión detallada del rendimiento y las incidencias actuales.
        """
        elements += Paragraph(intro_text, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        # Obtención de datos de la base de datos
        alarms_count = self.db.get_alarm_count()
        events_count = next(q.run() for q in self.queries if q._id == "get_events_count")["total"][0]
        logs_count = next(q.run() for q in self.queries if q._id == "get_logs_count")["total"][0]

        # Resumen de Indicadores Clave
        data = pd.DataFrame(columns=["Descripción", "Valor"], data=[
            ["Disponibilidad del Sistema", "99.9%"],
            ["Logs Procesados", format_number(logs_count, locale='es')],
            ["Eventos Procesados", format_number(events_count, locale='es')],
            ["Alarmas Activadas", format_number(alarms_count, locale='es')],
        ])

        table_style = self.style(self.tables_styles.DEFAULT)
        table = Table(data, style=table_style, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm)
        elements += table.render()

        elements += PageBreak()

        return elements

    def add_threat_analysis(self):
        style = self.style(self.paragraph_styles.SUB_TITLE_1)
        elements = ElementList()
        elements += Paragraph("Análisis de Amenazas", style)
        
        elements += Paragraph("Durante el período de reporte, se detectaron varios tipos de amenazas. La siguiente tabla muestra la distribución del número de eventos de amenazas por tipo y su frecuencia relativa.", self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

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
            {"Threat Type": "Access Failure", "Frequency": get_frequency("access failure")},
            {"Threat Type": "Authentication Failure", "Frequency": get_frequency("authentication failure")},
            {"Threat Type": "Suspicious Activity", "Frequency": get_frequency("suspicious")},
            {"Threat Type": "Vulnerability", "Frequency": get_frequency("vulnerability")},
            {"Threat Type": "Attack", "Frequency": get_frequency("attack")},
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

    def add_incident_response(self):
        style = self.style(self.paragraph_styles.SUB_TITLE_1)
        elements = ElementList()
        elements += Paragraph("Respuesta a Incidentes", style)

        elements += Paragraph("Desactivado temporalmente mientras se decide si el equipo del SOC va a poner los datos a mano o si simplemente no se añaden.", self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        elements += PageBreak()

        return elements

    def add_trends_and_comparatives(self):
        style = self.style(self.paragraph_styles.SUB_TITLE_1)
        elements = ElementList()
        elements += Paragraph("Tendencias y Comparativas", style)

        elements += Paragraph("En esta sección, se comparan los eventos procesados y los incidentes detectados durante el período actual con los períodos anteriores. Estas comparativas permiten identificar tendencias y evaluar la efectividad de las medidas implementadas.", self.style(self.paragraph_styles.SUB_TEXT_NORMAL))

        data = pd.DataFrame(columns=["Período", "Eventos Procesados", "Incidentes Detectados"], data=[
            ["Julio 2024", format_number(1200000, locale='es'), "45"],
            ["Junio 2024", format_number(1100000, locale='es'), "40"]
        ])
        table_style = self.style(self.tables_styles.DEFAULT)
        table = Table(data, style=table_style, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm)
        elements += table.render()
        elements += Spacer(1, 12)

        # Obtención de datos del histograma
        histo_success_df = next(q.run() for q in self.queries if q._id == "msgClassName_authentication_success_histogram")
        histo_failure_df = next(q.run() for q in self.queries if q._id == "msgClassName_authentication_failure_histogram")

        elements += ComparisonLine(histo_success_df, histo_failure_df, "key_as_string", "doc_count", title="Comparación de Eventos de Autenticación", xlabel="Fecha", ylabel="Cantidad de Eventos").plot()
        elements += Spacer(1, 12)

        elements += PageBreak()

        return elements

    def add_recommendations(self):
        style = self.style(self.paragraph_styles.SUB_TITLE_1)
        elements = ElementList()
        elements += Paragraph("Recomendaciones", style)
        
        elements += Paragraph("Basado en el análisis de los datos y la evaluación de las respuestas a incidentes, se proponen las siguientes recomendaciones para mejorar la seguridad y eficiencia del sistema.", self.style(self.paragraph_styles.TEXT_NORMAL))

        data = pd.DataFrame(columns=["Descripción", "Valor"], data=[
            ["Mejoras Propuestas", "Implementar autenticación multifactor en todos los sistemas"],
            ["Áreas Prioritarias", "Fortalecer la capacitación de los empleados sobre phishing"]
        ])
        table_style = self.style(self.tables_styles.DEFAULT)
        table = Table(data, style=table_style, mode='fit-full', indent=1.2 * cm, subtract=1.2 * cm)
        elements += table.render()
        elements += Spacer(1, 12)

        return elements

    def add_conclusion(self):
        style = self.style(self.paragraph_styles.TITLE_2)
        elements = ElementList()
        elements += Paragraph("Conclusión", style)
        
        text = """
        La operación del SIEM en Julio 2024 ha sido efectiva en detectar y mitigar amenazas, 
        aunque se recomienda seguir mejorando las medidas preventivas y de respuesta.
        """
        elements += Paragraph(text, self.style(self.paragraph_styles.SUB_TEXT_NORMAL))
        elements += Spacer(1, 12)

        return elements


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

# Check if Python version is 3.7 or higher
if not sys.version_info >= (3, 7):
    print("LogRhythm Report Tool requires Python 3.7 or higher.")
    sys.exit(1)

from modules.questions import select_entities, select_tables, select_charts, select_date_range

from modules.questions import ListReorder
from modules.components import Components
from modules.report import Report
from modules.database import MSQLServer
from modules.elastic import Elastic

import pandas as pd

from modules.questions import get_output_details, get_signature, get_client_details, use_template
from utils import get_file_name, execute_callbacks
from datetime import datetime

def main():
    debug_mode = False
    if "--debug" in sys.argv:
        debug_mode = True

    # Inicialización de Elastic y MSQLServer
    # Se crean instancias de las clases Elastic y MSQLServer
    elastic = Elastic()
    database = MSQLServer()

    # Selección de rango de fechas
    # La función select_date_range() devuelve una tupla con la fecha de inicio y fin
    (start, end) = select_date_range() if not debug_mode else (datetime(2024, 6, 1), datetime(2024, 6, 30))

    # Imprime el rango de fechas seleccionado en formato ISO 8601
    print("Rango de fechas seleccionado:")
    print(f"Desde {start.strftime('%Y-%m-%dT%H:%M:%SZ')} hasta {end.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print("")

    # Establecer el rango de fechas en las instancias de Elastic y MSQLServer
    elastic.set_date_range(start, end)
    database.set_date_range(start, end)

    # Selección de entidades
    # La función select_entities(database) devuelve una lista de entidades seleccionadas de la base de datos
    entities = select_entities(database) if not debug_mode else pd.DataFrame(data = { 'EntityID': [4], 'FullName': ['Farmatodo'] })

    # Imprime las entidades seleccionadas
    print("Entidades seleccionadas:")
    print(entities)
    print("")

    # Establecer las entidades seleccionadas en la base de datos
    database.set_entity_ids(entities)
    elastic.set_entity_ids(entities)
    
    # Cargar las consultas desde un archivo
    # La función load_queries() carga consultas desde la ruta especificada
    queries = elastic.load_queries("./querys/elastic")

    default_signature = {
        "title": "",
        "author": "Netready Solutions",
        "subject": "Netready Solutions - LogRhythm",
        "keywords": ["LogRhythm", "Netready Solutions", "Report", "Confidential"],
        # Static
        "producer": "LogRhythm Report Tool - github.com/Undead34",
        "creator": "LogRhythm Report Tool - @Undead34"
    }

    signature = get_signature(default_signature) if not debug_mode else default_signature

    (name, logo) = get_client_details() if not debug_mode else ('Farmatodo', './assets/images/clients/farmatodo/logo.png')
    
    signature["client_name"] = name

    output_path, filename_format = get_output_details() if not debug_mode else ("./output", "{client_name} - {stime}")
    
    output = get_file_name(output_path, filename_format, signature)

    signature["client_logo"] = logo

    # Generate Report
    report = Report(queries, database, output, signature)
    components = Components(report)

    report.elements += components.cover_page(signature, name, logo)

    elements = []

    if use_template():
        from reportlab.platypus import PageBreak, Spacer, Paragraph, TableStyle, ListFlowable, ListItem, Indenter
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        from modules.template.theme import ParagraphStyles
        from utils import ElementList

        e = ElementList()

        get_style = components.theme.get_style
        N = components.theme.replace_bold_with_font
        styles = ParagraphStyles
        charts = components.charts
        
        def create_list(items, style):
            bullet_color = components.theme.NetReadyBlue  # Color azul para las viñetas
            list_elements = ListFlowable(
                [ListItem(Paragraph(N(item), style), leftIndent=1 * cm) for item in items],
                bulletType='bullet',
                bulletColor=bullet_color,
                spaceBefore=0,  # Ajustar espacio antes
                spaceAfter=0,  # Ajustar espacio después
                bulletFontName='Arial-Narrow'
            )
            return list_elements

        # Introducción
        e += Paragraph("Introducción".upper(), get_style(styles.NR_TITULO_1))

        # Objetivo del Informe
        e += Paragraph("1. Objetivo del Informe", get_style(styles.NR_TITULO_2))

        e += Paragraph(N("""
        **Propósito**: El propósito de este informe es proporcionar una visión detallada y automatizada del estado del Sistema de Gestión de Información y Eventos de Seguridad (SIEM),
                destacando los aspectos clave relacionados con la seguridad, el rendimiento y la conformidad.
        """), get_style(styles.NR_TEXTO_1))

        e += Paragraph(N("""
        **Alcance**: Este informe cubre la actividad del SIEM durante el periodo especificado,
                        incluyendo la identificación de atacantes, vulnerabilidades, alarmas, violaciones de cumplimiento,
                        fallas operativas, violaciones de auditoría, detalles de logs, estadísticas de componentes y resúmenes automáticos.
        """), get_style(styles.NR_TEXTO_1))

        # Agregando más detalles al informe
        e += Paragraph(N("""
        **Metodología**: Los datos presentados en este informe han sido recopilados y analizados utilizando herramientas automatizadas
                que integran y correlacionan información de múltiples fuentes. Los gráficos y tablas incluidos son el resultado
                de análisis estadísticos diseñados para resaltar tendencias significativas y puntos de atención críticos.
        """), get_style(styles.NR_TEXTO_1))

        e += Paragraph(N("""
        **Estructura del Informe**: Este informe se divide en varias secciones clave:
        """), get_style(styles.NR_TEXTO_1))

        # Crear lista de secciones
        sections = [
            "**Indicadores de cumplimiento de SLA y Tiempos de Gestión**: Un análisis detallado de los indicadores de nivel de servicio (SLA) y tiempos de respuesta para la gestión de incidentes y eventos.",
            "**Análisis de Eventos**: Un desglose de los eventos capturados por el SIEM, categorizados por tipo, gravedad y fuente.",
            "**Detección de Amenazas**: Información sobre amenazas detectadas, incluyendo atacantes identificados, métodos de ataque y medidas de mitigación implementadas.",
            "**Conformidad y Auditoría**: Evaluación del cumplimiento de políticas de seguridad y auditorías realizadas durante el periodo.",
            "**Recomendaciones**: Sugerencias para mejorar la postura de seguridad basada en los hallazgos del análisis."
        ]

        e += create_list(sections, get_style(styles.NR_LISTA))

        # Página de indicadores de cumplimiento de SLA
        e += PageBreak()
        e += Paragraph(N("Indicadores de cumplimiento de SLA y Tiempos de Gestión").upper(), get_style(styles.NR_TITULO_1))

        components.charts.events_histogram_by_month_by_msg_class_name()

        e += components.tables.table_ttd_ttr_by_msg_class_name()

        e += components.charts.events_histogram_by_month()

        elements = e
    else:
        # Tables
        tables = components.get_tables()
        selected_tables = select_tables(tables)

        # Charts
        charts = components.get_charts()
        selected_charts = select_charts(charts)

        # Combinar DataFrames y reordenar
        unordered_elements = pd.concat([selected_tables, selected_charts], ignore_index=True)

        elements = ListReorder(unordered_elements).reorder()

    # Ejecutar callbacks y construir el reporte
    if (isinstance(elements, pd.DataFrame)):
        elements = execute_callbacks(elements)
        
    for element in elements:
        report.elements += element

    report.build()
    print("✅ [Reporte generado]\nRuta de salida del archivo:", output)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
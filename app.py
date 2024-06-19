#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys

# Check if Python version is 3.7 or higher
if not sys.version_info >= (3, 7):
    print("LogRhythm Report Tool requires Python 3.7 or higher.")
    sys.exit(1)

import pandas as pd

from modules.components import Components
from modules.database import MSQLServer
from modules.elastic import Elastic
from modules.report import Report

from modules.questions import (
    select_entities,
    select_tables,
    select_charts,
    select_date_range,
    ListReorder,
)
from modules.questions import get_output_details, get_signature, get_client_details, use_template
from utils import get_file_name, execute_callbacks


def main():
    # Inicialización de Elastic y MSQLServer
    # Se crean instancias de las clases Elastic y MSQLServer
    elastic = Elastic()
    database = MSQLServer()

    # Selección de rango de fechas
    # La función select_date_range() devuelve una tupla con la fecha de inicio y fin
    (start, end) = select_date_range()

    # Imprime el rango de fechas seleccionado en formato ISO 8601
    print("Rango de fechas seleccionado:")
    print(f"Desde {start.strftime('%Y-%m-%dT%H:%M:%SZ')} hasta {end.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print("")

    # Establecer el rango de fechas en las instancias de Elastic y MSQLServer
    elastic.set_date_range(start, end)
    database.set_date_range(start, end)

    # Selección de entidades
    # La función select_entities(database) devuelve una lista de entidades seleccionadas de la base de datos
    entities = select_entities(database)

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

    signature = get_signature(default_signature)

    (name, logo) = get_client_details()
    signature["client_name"] = name

    output_path, filename_format = get_output_details()
    output = get_file_name(output_path, filename_format, signature)

    signature["client_logo"] = logo

    # Generate Report
    report = Report(queries, database, output, signature)
    components = Components(report)

    report.elements += components.cover_page(signature, name, logo)

    elements = []

    if use_template():
        # Informe General de Seguridad SIEM
        from reportlab.platypus import PageBreak, Image, Spacer, Paragraph, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        from modules.template.theme import ParagraphStyles
        from utils import ElementList

        e = ElementList()

        get_style: callable = components.theme.get_style
        N: callable = components.theme.replace_bold_with_font
        styles = ParagraphStyles
        charts = components.charts

        e += Paragraph("Introducción".upper(), get_style(styles.NR_TITULO_1))
        
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

        e += PageBreak()

        e += Paragraph("Top Atacantes".upper(), get_style(styles.NR_TITULO_1))

        e += charts.bar_chart_top_attackers()
        e += charts.pareto_chart_top_attackers()


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
    elements = execute_callbacks(elements) if not isinstance(elements, list) and elements else elements

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



        # # Obtener la tabla con el ID específico
        # table = next((q.run() for q in queries if q._id == "cdc64feb-bcd3-4675-be78-44f8d6f2af9d"), pd.DataFrame())

        # # Convertir columnas y valores en una lista
        # table_data = [table.columns.to_list()] + table.values.tolist()
        
        # # Agregar encabezado de índice
        # table_data[0] = ["Index", "Origin IP", "Count"]
        
        # # Insertar el índice en cada fila de datos
        # for i, row in enumerate(table_data[1:], start=1):
        #     row.insert(0, i)

        # # Uso de la función _table_maker con las nuevas opciones
        # e += components.tables._table_maker(
        #     table_data,
        #     mode="fit-full",
        #     padding=10,
        #     include_totals=True,
        #     totals_columns=[2]  # Especifica la columna 'Count' para sumar
        # )


        # e += charts.pareto_chart_top_attackers(table)

        # Alarms
        # e += charts.trends_in_alarm_activation_graph()
        # e += charts.stacked_bar_chart_by_alarm_type()
        # e += charts.stacked_bar_chart_by_alarm_status()
        # e += charts.heatmap_alarms_by_day_and_hour()
        # e += charts.scatter_plot_time_to_detection()

        # data = next((q.run() for q in queries if q._id == "1d0ece15-8f1b-4c45-ae38-a9c1f06761ba"), pd.DataFrame())


        # elements += charts.box_plot_risk_distribution(data)
        # elements += charts.pie_chart_reporting_devices(data)

        # for q in queries:
        #     if q._id != "cdc64feb-bcd3-4675-be78-44f8d6f2af9d":
        #         print(q.run())
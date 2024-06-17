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

    for package in queries:
        if package._type != "2":
            continue

        df = package.run()
        import json
        print(json.dumps(package._query, indent=2))
        # print(f"Resultados para la consulta {package._name}:")
        # print(df)

    return

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

    elements = None

    if use_template():
        print("")
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
    elements = execute_callbacks(elements) if elements else []

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

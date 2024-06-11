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
from modules.questions import get_output_details, get_signature, get_client_details
from utils import get_file_name, execute_callbacks


def main():
    # Elastic Init
    elastic = Elastic()
    querys = elastic.load_queries("./querys")

    # Database Init
    db = MSQLServer()
    print("Bienvenido a «LogRhythm Report Tool», para crear su reporte primero tenemos que configurar algunas cosas.\n")

    entities = select_entities(db)
    db.set_entity_ids(entities)

    print("Entidades seleccionadas:")
    print(entities)
    print("")

    dates = select_date_range()
    start, end = db.set_date_range(dates)

    print("Rango de fechas seleccionado:")
    print(f"Desde {start} hasta {end}")
    print("")

    default_signature = {
        "title": "",
        "author": "Netready Solutions",
        "subject": "Netready Solutions - LogRhythm",
        "keywords": ["LogRhythm", "Netready Solutions", "Report", "Confidential"],
        # Static
        "producer": "LogRhythm Report Tool - github.com/Undead34",
        "creator": "LogRhythm Report Tool - @Undead34",
    }

    signature = get_signature(default_signature)

    (name, logo) = get_client_details()
    signature["client_name"] = name

    output_path, filename_format = get_output_details()
    output = get_file_name(output_path, filename_format, signature)

    signature["client_logo"] = logo

    # Generate Report
    report = Report(querys, db, output, signature)
    components = Components(report)

    report.elements += components.cover_page(signature, name, logo)

    # Tables
    tables = components.get_tables()
    selected_tables = select_tables(tables)

    # Charts
    charts = components.get_charts()
    selected_charts = select_charts(charts)

    # Combinar DataFrames y reordenar
    unordered_elements = pd.concat([selected_tables, selected_charts], ignore_index=True)

    ordered_elements = ListReorder(unordered_elements).reorder()

    # Ejecutar callbacks y construir el reporte
    elements = execute_callbacks(ordered_elements)

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

# table = querys[0].run()
# # print(table)
# # table = table.groupby(['rootEntityName', 'originIp', 'impactedIp', 'msgSourceTypeName', 'severity', 'msgClassName', 'directionName']).size().reset_index(name='Counts')
# # table = table.sort_values(by='Counts', ascending=False).reset_index(0)
# # print(table)

# # Agrupar y agregar los datos
# chart_1 = table.groupby('originIp').sum().reset_index()
# chart_1 = chart_1.sort_values(by='Counts', ascending=False).reset_index(drop=True)
# return
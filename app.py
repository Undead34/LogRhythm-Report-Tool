#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys

# Check if Python version is 3.7 or higher
if not sys.version_info >= (3, 7):
    print("LogRhythm Report Tool requires Python 3.7 or higher.")
    sys.exit(1)

from modules.components import Components
from modules.database import MSQLServer
from modules.elastic import Elastic
from modules.report import Report

from modules.questions import get_output_details, get_signature, select_entities, get_client_details, select_tables
from utils import get_file_name, execute_callbacks, clear_console


def main():
    # Elastic Init
    elastic = Elastic()
    elastic.loadQuerys("./querys")
    querys = elastic.run()

    # Database Init
    db = MSQLServer()
    print("Bienvenido a «LogRhythm Report Tool», para crear su reporte primero tenemos que configurar algunas cosas.\n")

    entities = select_entities(db)
    db.set_entity_ids(entities)
    
    print("Entidades seleccionadas:")
    print(entities)
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

    tables = components.get_tables()

    selected_tables = select_tables(tables)

    elements_tables = execute_callbacks(selected_tables)

    for element in elements_tables:
        report.elements += element

    report.build()
    print("✅ [Reporte generado]\nRuta de salida del archivo:", output)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)

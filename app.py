#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

# Check if Python version is 3.7 or higher
if not sys.version_info >= (3, 7):
    print("LogRhythm Report Tool requires Python 3.7 or higher.")
    sys.exit(1)

from utils import constants, get_file_name
from modules.report import Report
from modules.elastic import Elastic


# La estrategia más eficiente es preparar el terreno y hacer las consultas mientras
# liberas memoria, así también puedes tomar decisiones sobre la marcha.
def bootstrap():
    elastic = Elastic()
    elastic.loadQuerys("./querys")
    querys = elastic.run()

    signature = {
        "author": "Netready Solutions",
        "producer": "LogRhythm Report Tool - Gabriel Maizo/NetReady",
        "creator": "Netready Solutions © 2024",
        "subject": "Netready Solutions - LogRhythm",
        "title": "Hola",
        "keywords": ["LogRhythm", "Netready Solutions", "Report", "Confidential"],
    }

    output = get_file_name("{title} - {stime}", signature)

    report = Report(querys, output, signature)
    report.build()
    print("Reporte generado: ", output)


if __name__ == "__main__":
    try:
        bootstrap()
    except Exception as e:
        print(e)
        sys.exit(1)

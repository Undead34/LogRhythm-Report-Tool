#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

# Check if Python version is 3.7 or higher
if not sys.version_info >= (3, 7):
    print("LogRhythm Report Tool requires Python 3.7 or higher.")
    sys.exit(1)

# from utils.test import check_environ_vars, check_permisions, check_first_start, check_connection
# from utils.setup import setup

from modules.report import Report
from modules.elastic import Elastic

def bootstrap():
    elastic = Elastic()
    elastic.loadQuerys("./querys")
    elastic.run()

    report = Report()


if __name__ == "__main__":
    try:
        bootstrap()
    except Exception as e:
        print(e)
        sys.exit(1)

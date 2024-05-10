from elasticsearch import Elasticsearch
from prettytable import PrettyTable

import glob
import json
import os


class Package():
    def __init__(self, elastic) -> None:
        self._elastic: Elastic = elastic
        self.query = None

    def run(self):
        self._elastic.search(self.query)

    def parser():
        pass

class Elastic():
    def __init__(self) -> None:
        self._esearch = Elasticsearch(["http://localhost:9200"])
        self._querys = []

    def loadQuerys(self, folder: str) -> None:
        folder = os.path.realpath(folder)

        if not os.path.exists(folder):
            raise FileNotFoundError("Por favor, introduce una ruta válida")

        if not os.path.isdir(folder):
            raise NotADirectoryError("Por favor, introduce una ruta válida")

        json_files = glob.glob(os.path.join(
            folder, '**/*.json'), recursive=True)

        try:
            for file in json_files:
                with open(file, "r") as f:
                    data = f.read()
                    data = json.loads(data)

                self._querys.append(data)
        except Exception as e:
            print("An error occurred while executing the {0} file, please check: {1}".format(
                file, e))

    def run(self) -> list[Package]:
        querys = []

        for q in self._querys:
            p = Package(self)
            p.query = q
            querys.append(p)

        return querys

    def search(self, query: dict) -> None:
        config: dict = query.get("config")
        query: dict = query.get("query")

        r: dict = self._esearch.search(index="logs-*", body=query)

        return r


class Normalizer():
    def __init__(self) -> None:
        pass

    @staticmethod
    def table():
        pass

    @staticmethod
    def set_xpath(xpath: str, element):
        paths = xpath.split(".")

        for p in paths:
            if element is None:
                break
            element = element.get(p, None)

        return element

    @staticmethod
    def set_xpath(xpath: str, element, value):
        paths = xpath.split(".")
        for p in paths[:-1]:  # Recorremos todos los elementos excepto el último
            if element is None:
                break
            element = element.get(p, None)

        if element is not None:
            # Establecemos el valor en el último elemento del camino
            element[paths[-1]] = value

# data = Normalizer.set_xpath(config.get("xpath"), r)
# print(data)

# # table = PrettyTable()

# # table.field_names = ["Key", "#"]
# # for x in data:
# #     table.add_row([x.get("key"), x.get("doc_count")])

# # print(table)

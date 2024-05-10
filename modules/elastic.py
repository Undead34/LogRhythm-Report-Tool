from elasticsearch import Elasticsearch
import os
import glob
import json


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

    def run(self) -> None:
        for q in self._querys:
            self.search(q)

    def search(self, query: dict) -> None:
        r: dict = self._esearch.search(index="logs-*", body=query)
        hits: dict = r.get("hits")
        hist_values: list = hits.get("hits")
        print(hist_values[0])

import os
import glob
import json
import pandas as pd
from elasticsearch import Elasticsearch


class Package:
    def __init__(self, elastic: 'Elastic', query: dict) -> None:
        self._es = elastic._es
        self._name = query.get("name")
        self._mode = query.get("mode")
        self._index = query.get("index")
        self._query = query.get("query")
        self._description = query.get("description")

    def run(self) -> pd.DataFrame:
        if not self._index or not self._query:
            raise ValueError("Index and query must be provided.")

        index_str = ",".join(self._index) if isinstance(self._index, list) else self._index
        data = None

        if self._mode == "multi":
            response = self._es.msearch(index=index_str, body=self._query, _source=True)
            data = self._extract_hits(response)
        else:
            response = self._es.search(index=index_str, body=self._query, _source=True)
            data = self._extract_hits(response)
        
        # Extract the 'fields' dictionary from each hit and flatten it
        all_fields = [hit['fields'] for hit in data]
        
        # Ensure all field dictionaries have the same keys, fill missing keys with None
        all_keys = set(key for fields in all_fields for key in fields)
        standardized_fields = []
        for fields in all_fields:
            standardized_fields.append({key: fields.get(key, [None]) for key in all_keys})

        # Create DataFrame from standardized fields
        df = pd.DataFrame(standardized_fields)
        
        # Flatten lists to single values where possible
        df = df.apply(lambda col: col.map(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x))

        return df

    def _extract_hits(self, response):
        if "responses" in response:  # msearch response
            hits = []
            for res in response["responses"]:
                hits.extend(res.get("hits", {}).get("hits", []))
            return hits
        else:  # search response
            return response.get("hits", {}).get("hits", [])


class Elastic:
    def __init__(self, host: str = "http://localhost:9200") -> None:
        self._es = Elasticsearch([host])

    def load_queries(self, folder: str) -> list[Package]:
        folder_path = os.path.realpath(folder)

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"La ruta {folder_path} no existe.")

        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"{folder_path} no es un directorio.")

        json_files = glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)

        queries = []

        for file in json_files:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                queries.append(Package(self, data))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al procesar el archivo {file}: {e}")
        
        return queries

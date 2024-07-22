import os
import glob
import json
import pandas as pd
from datetime import datetime
from elasticsearch import Elasticsearch

from src.utils.logger import get_logger
from .package import Package

class Elastic:
    def __init__(self, host: str = "http://localhost:9200", timeout: int = 30, max_retries: int = 10, retry_on_timeout: bool = True) -> None:
        self._es = Elasticsearch(
            [host],
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout
        )
        self._date_range = None
        self._entity_ids = None
        self.logger = get_logger()
    
    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        self._date_range = (start_date, end_date)

    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self._entity_ids = entity_ids

    def export_to_csv(self, directory: str, output: str) -> None:
        if not os.path.exists(output):
            os.makedirs(output, True)
        
        queries = self.load_queries(directory)
        for query in queries:
            df = query.run()
            if not df.empty:
                self.logger.info(f"Exportando {query._name}")
                file_name = f"{query._name}_elastic.csv"
                df.to_csv(os.path.join(output, file_name), index=False)

    def load_queries(self, folder: str) -> list['Package']:
        folder_path = os.path.realpath(folder)
        self._validate_folder_path(folder_path)
        json_files = glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)
        queries = []
        date_range = self._get_epoch_millis_range()

        for file in json_files:
            data = self._load_json_file(file)
            if not self._is_valid_data(data):
                self.logger.warn(f"Formato de datos no reconocido en el archivo {file}.")
                continue
            try:
                data['query'] = self._replace_placeholders(data, date_range)
                queries.append(Package(self, data))
            except KeyError as e:
                self.logger.error(f"Error al procesar el archivo {file}: {e}")
        
        return queries

    def _replace_placeholders(self, data: dict, date_range: dict) -> dict:
        query_str = json.dumps(data['query'])
        
        # Reemplazo del rango de fechas
        date_replacement = data['processing_policy']['date_range_replacement']
        query_str = query_str.replace(date_replacement['gte_placeholder'], str(date_range['gte']))
        query_str = query_str.replace(date_replacement['lte_placeholder'], str(date_range['lte']))
        
        # Reemplazo de entity_ids
        entity_replacement = data['processing_policy']['entity_ids_replacement']
        entity_ids_list = [str(id) for id in self._entity_ids['EntityID']]
        
        if entity_replacement['type'] == "term":
            terms_query = json.dumps({"terms": {entity_replacement['field']: entity_ids_list}})
            query_str = query_str.replace(f'"{entity_replacement["placeholder"]}"', terms_query)
        elif entity_replacement['type'] == "match":
            entity_id_matches = [{'match': {entity_replacement['field']: str(id)}} for id in self._entity_ids['EntityID']]
            entity_id_placeholder = f'[{{"match": {{"{entity_replacement["field"]}": "{entity_replacement["placeholder"]}"}}}}]'
            query_str = query_str.replace(entity_id_placeholder, json.dumps(entity_id_matches))
        elif entity_replacement['type'] == "query_string":
            entity_ids_str = " OR ".join(entity_ids_list)
            query_str = query_str.replace(entity_replacement['placeholder'], f'{entity_replacement["field"]}: ({entity_ids_str})')

        return self._load_json_str(query_str)

    def _load_json_str(self, json_str: str) -> dict:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error("Error al decodificar JSON:", e)
            self.logger.error("Query string con error:", json_str)
            raise

    def _validate_folder_path(self, folder_path: str):
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"La ruta {folder_path} no existe.")
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"{folder_path} no es un directorio.")

    def _load_json_file(self, file: str) -> dict:
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error al procesar el archivo {file}: {e}")
            return {}

    def _is_valid_data(self, data: dict) -> bool:
        return 'query' in data and 'query' in data['query'] and 'processing_policy' in data

    def _convert_to_epoch_millis(self, date_obj: datetime) -> int:
        return int(date_obj.timestamp() * 1000) if date_obj else None

    def _get_epoch_millis_range(self) -> dict:
        if self._date_range:
            start_date, end_date = self._date_range
            return {
                "gte": self._convert_to_epoch_millis(start_date),
                "lte": self._convert_to_epoch_millis(end_date),
                "format": "epoch_millis"
            }
        return {}


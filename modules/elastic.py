import os
import glob
import json
import pandas as pd
from datetime import datetime
from elasticsearch import Elasticsearch

class Package:
    def __init__(self, elastic_instance, data):
        self.elastic_instance = elastic_instance
        self.data = data

class Elastic:
    def __init__(self, host: str = "http://localhost:9200") -> None:
        """
        Inicializa la instancia de ElasticSearch con el host proporcionado.
        """
        self._es = Elasticsearch([host])
        self._date_range = None
        self._entity_ids = None

    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """
        Establece el rango de fechas para las consultas.
        Convierte las fechas a formato datetime y asegura que el tiempo final sea 23:59:59.
        """
        self._date_range = (start_date, end_date)

    def _convert_to_epoch_millis(self, date_obj: datetime) -> int:
        """
        Convierte un objeto de fecha a epoch milliseconds.
        """
        if date_obj:
            epoch_millis = int(date_obj.timestamp() * 1000)
            return epoch_millis
        return None

    def get_epoch_millis_range(self) -> dict:
        """
        Retorna el rango de fechas en formato epoch milliseconds, adecuado para consultas a Elasticsearch.
        """
        if self._date_range:
            start_date, end_date = self._date_range
            return {
                "gte": self._convert_to_epoch_millis(start_date),
                "lte": self._convert_to_epoch_millis(end_date),
                "format": "epoch_millis"
            }
        return {}
    
    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self._entity_ids = entity_ids

    def _replace_placeholders_type_1(self, data: dict, date_range: dict) -> dict:
        """
        Reemplaza placeholders para el tipo 1 de JSON.
        """
        query_str = json.dumps(data['query'])
        
        # Reemplazar los placeholders de fechas
        query_str = query_str.replace('{{gte}}', str(date_range['gte']))
        query_str = query_str.replace('{{lte}}', str(date_range['lte']))

        # Crear la lista de objetos match para entityId
        entity_id_matches = [{'match': {'entityId': str(id)}} for id in self._entity_ids['EntityID']]
        
        # Reemplazar el placeholder de entity_ids
        entity_id_placeholder = r'[{"match": {"entityId": "{{entity_ids}}"}}]'
        query_str = query_str.replace(entity_id_placeholder, json.dumps(entity_id_matches))

        try:
            # Actualizar el query original
            return json.loads(query_str)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            print("Query string con error:", query_str)
            raise

    def load_queries(self, folder: str) -> list['Package']:
        """
        Carga todas las consultas desde archivos JSON en la carpeta especificada.
        Retorna una lista de instancias de Package.
        """
        folder_path = os.path.realpath(folder)

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"La ruta {folder_path} no existe.")

        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"{folder_path} no es un directorio.")

        json_files = glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)

        queries = []
        date_range = self.get_epoch_millis_range()

        for file in json_files:
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                # Intentar reemplazar los placeholders con los valores de epoch millis
                try:
                    if 'query' in data and 'query' in data['query'] and 'type' in data:
                        if data['type'] == "1":
                            data['query'] = self._replace_placeholders_type_1(data, date_range)
                except KeyError as e:
                    print(f"Error al reemplazar los valores de fecha o entityId en el archivo {file}: {e}")
                
                queries.append(Package(self, data))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al procesar el archivo {file}: {e}")
        
        return queries

class Package:
    def __init__(self, elastic: 'Elastic', data: dict) -> None:
        """
        Inicializa un paquete de consulta con los datos proporcionados.
        """
        self._es = elastic._es
        self._id = data.get("id")
        self._name = data.get("name")
        self._mode = data.get("mode")
        self._index = data.get("index")
        self._query = data.get("query")
        self._description = data.get("description")
        self._aggregation_result = data.get("aggregation_result", False)

    def run(self) -> pd.DataFrame:
        """
        Ejecuta la consulta y retorna los resultados en forma de DataFrame de pandas.
        """
        if not self._id or not self._index or not self._query:
            raise ValueError("ID, index, and query must be provided.")

        index_str = ",".join(self._index) if isinstance(self._index, list) else self._index
        data = None
        
        if self._mode == "multi":
            response = self._es.msearch(index=index_str, body=self._query, _source=True)
            data = self._extract_hits(response)
        else:
            response = self._es.search(index=index_str, body=self._query, _source=True)
            if self._aggregation_result:
                data = self._extract_aggregations(response)
            else:
                data = self._extract_hits(response)
        
        if data is None:
            raise ValueError("No data found in the response.")
        
        if len(data) == 0:
            return pd.DataFrame()
        
        # Si la respuesta contiene datos de hits (documentos encontrados)
        if isinstance(data[0], dict) and "_source" in data[0]:
            # Extraer los campos '_source' de cada hit y crear un DataFrame
            all_fields = [hit['_source'] for hit in data]
            df = pd.DataFrame(all_fields)
        
        # Si la respuesta contiene datos de agregación (resultados de aggregaciones)
        elif isinstance(data[0], dict) and "key" in data[0] and "doc_count" in data[0]:
            df = pd.DataFrame(data)
            df.rename(columns={"key": "msgSourceTypeName", "doc_count": "count"}, inplace=True)
        
        elif "fields" in data[0] and isinstance(data[0]["fields"], dict):
            fields = self._extract_fields(data)
            # Create DataFrame from standardized fields
            df = pd.DataFrame(fields)
            
            # Flatten lists to single values where possible
            df = df.apply(lambda col: col.map(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x))
        else:
            raise ValueError("Unrecognized data format in the response.")
        
        return df
    
    def _extract_fields(self, response):
        # Extract the 'fields' dictionary from each hit and flatten it
        all_fields = [hit['fields'] for hit in response]
        
        # Ensure all field dictionaries have the same keys, fill missing keys with None
        all_keys = set(key for fields in all_fields for key in fields)
        standardized_fields = []
        for fields in all_fields:
            standardized_fields.append({key: fields.get(key, [None]) for key in all_keys})

        return standardized_fields

    def _extract_hits(self, response):
        """
        Extrae los hits (documentos encontrados) de la respuesta de Elasticsearch.
        """
        if "responses" in response:  # Respuesta de msearch
            hits = []
            for res in response["responses"]:
                hits.extend(res.get("hits", {}).get("hits", []))
            return hits
        else:  # Respuesta de search
            return response.get("hits", {}).get("hits", [])

    def _extract_aggregations(self, response):
        """
        Extrae los resultados de las agregaciones de la respuesta de Elasticsearch.
        """
        aggregations = response.get("aggregations", {})
        if aggregations:
            buckets = aggregations.get("3", {}).get("buckets", [])
            return buckets
        else:
            return []
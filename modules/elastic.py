import os
import glob
import json
import pandas as pd
from datetime import datetime
from elasticsearch import Elasticsearch


class Elastic:
    def __init__(self, host: str = "http://localhost:9200", timeout: int = 30, max_retries: int = 10, retry_on_timeout: bool = True) -> None:
        """
        Inicializa la instancia de ElasticSearch con el host proporcionado.
        """
        self._es = Elasticsearch(
            [host],
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout
        )
        self._date_range = None
        self._entity_ids = None
    
    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """
        Establece el rango de fechas para las consultas.
        Convierte las fechas a formato datetime y asegura que el tiempo final sea 23:59:59.
        """
        self._date_range = (start_date, end_date)

    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self._entity_ids = entity_ids


    def load_queries(self, folder: str) -> list['Package']:
        """
        Carga todas las consultas desde archivos JSON en la carpeta especificada.
        Retorna una lista de instancias de Package.
        """
        folder_path = os.path.realpath(folder)
        self._validate_folder_path(folder_path)

        json_files = glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)

        queries = []
        date_range = self._get_epoch_millis_range()

        for file in json_files:
            data = self._load_json_file(file)
            if not self._is_valid_data(data):
                print(f"Formato de datos no reconocido en el archivo {file}.")
                continue
            
            try:
                data['query'] = self._process_query_by_type(data, date_range)
                queries.append(Package(self, data))
            except KeyError as e:
                print(f"Error al procesar el archivo {file}: {e}")
        
        return queries

    def _convert_to_epoch_millis(self, date_obj: datetime) -> int:
        """
        Convierte un objeto de fecha a epoch milliseconds.
        """
        if date_obj:
            epoch_millis = int(date_obj.timestamp() * 1000)
            return epoch_millis
        return None

    def _get_epoch_millis_range(self) -> dict:
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

    def _validate_folder_path(self, folder_path: str):
        """
        Valida si la ruta proporcionada es una carpeta existente.
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"La ruta {folder_path} no existe.")
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"{folder_path} no es un directorio.")

    def _load_json_file(self, file: str) -> dict:
        """
        Carga y retorna el contenido de un archivo JSON.
        """
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al procesar el archivo {file}: {e}")
            return {}

    def _is_valid_data(self, data: dict) -> bool:
        """
        Verifica si los datos cargados son válidos.
        """
        return 'query' in data and 'query' in data['query'] and 'type' in data

    def _process_query_by_type(self, data: dict, date_range: tuple) -> dict:
        """
        Procesa la consulta según su tipo.
        """
        if data['type'] == "1":
            return self._replace_placeholders_type_1(data, date_range)
        elif data['type'] == "2":
            return self._replace_placeholders_type_2(data, date_range)
        # Agrega más tipos aquí según sea necesario
        else:
            raise ValueError(f"Tipo de datos no reconocido: {data['type']}")

    def _replace_placeholders_type_1(self, data: dict, date_range: tuple) -> dict:
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

    def _replace_placeholders_type_2(self, data: dict, date_range: tuple) -> dict:
        """
        Reemplaza los marcadores de posición para consultas de tipo 2.
        """
        query_str = json.dumps(data['query'])
        
        # Reemplazar los placeholders de fechas
        query_str = query_str.replace('{{gte}}', str(date_range['gte']))
        query_str = query_str.replace('{{lte}}', str(date_range['lte']))

        # Reemplazar los entityId en el query_string
        entity_ids_str = " || ".join([str(id) for id in self._entity_ids['EntityID']])
        query_str = query_str.replace('{{entity_ids}}', f'entityId: ({entity_ids_str})')

        try:
            # Actualizar el query original
            return json.loads(query_str)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            print("Query string con error:", query_str)
            raise

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
        self._type = data.get("type")

    def run(self) -> pd.DataFrame:
        """
        Ejecuta la consulta y retorna los resultados en forma de DataFrame de pandas.
        """
        self._validate_query_parameters()

        index_str = ",".join(self._index) if isinstance(self._index, list) else self._index
        response = self._execute_query(index_str)

        if response is None:
            raise ValueError("No data found in the response.")

        hits = self._extract_hits(response)
        if self._aggregation_result:
            aggregations = self._extract_aggregations(response)
            if hits:
                df_hits = self._create_dataframe_from_hits(hits)
            else:
                df_hits = pd.DataFrame()

            if aggregations:
                df_aggs = self._create_dataframe(aggregations)
                if self._type == "2":
                    df_aggs = self._rename_columns(df_aggs)  # Renombrar columnas solo para tipo 2
            else:
                df_aggs = pd.DataFrame()

            if not df_hits.empty and not df_aggs.empty:
                df = pd.concat([df_hits, df_aggs], axis=1)
            elif not df_hits.empty:
                df = df_hits
            else:
                df = df_aggs
        else:
            df = self._create_dataframe_from_hits(hits)

        # Normalizar valores de arrays a valores simples si solo tienen un elemento
        df = self._normalize_array_values(df)

        return df

    def _validate_query_parameters(self):
        """
        Valida que los parámetros esenciales de la consulta estén presentes.
        """
        if not self._id or not self._index or not self._query:
            raise ValueError("ID, index, and query must be provided.")

    def _execute_query(self, index_str: str):
        """
        Ejecuta la consulta contra Elasticsearch y retorna la respuesta.
        """
        if self._mode == "multi":
            return self._es.msearch(index=index_str, body=self._query, _source=True)
        else:
            return self._es.search(index=index_str, body=self._query, _source=True)

    def _process_response(self, response):
        """
        Procesa la respuesta de Elasticsearch y extrae los datos relevantes.
        """
        if self._aggregation_result:
            return self._extract_aggregations(response)
        else:
            return self._extract_hits(response)

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
        if not aggregations:
            return []

        aggs_key = list(self._query['aggs'].keys())[0]  # Obtiene la primera clave de agregación
        aggs = self._query['aggs'][aggs_key]

        if 'terms' in aggs:
            return self._extract_terms_aggregations(aggregations, aggs_key)
        elif 'date_histogram' in aggs:
            return self._extract_date_histogram_aggregations(aggregations, aggs_key)
        elif 'aggs' in aggs:
            return self._extract_complex_aggregations(aggregations, aggs_key)
        else:
            raise ValueError("Unsupported aggregation type")

    def _extract_terms_aggregations(self, aggregations, aggs_key):
        """
        Extrae los resultados de una agregación de términos.
        """
        buckets = aggregations.get(aggs_key, {}).get("buckets", [])
        return buckets

    def _extract_date_histogram_aggregations(self, aggregations, aggs_key):
        """
        Extrae los resultados de una agregación de histograma de fechas.
        """
        buckets = aggregations.get(aggs_key, {}).get("buckets", [])
        return buckets

    def _extract_complex_aggregations(self, aggregations, aggs_key):
        """
        Extrae los resultados de una agregación compleja con sub-agregaciones.
        """
        buckets = aggregations.get(aggs_key, {}).get("buckets", [])
        return buckets

    def _create_dataframe(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los datos extraídos.
        """
        if isinstance(data[0], dict) and "_source" in data[0]:
            return self._create_dataframe_from_hits(data)
        elif isinstance(data[0], dict) and "key" in data[0] and "doc_count" in data[0]:
            aggs_key = list(self._query['aggs'].keys())[0]
            aggs = self._query['aggs'][aggs_key]

            if 'terms' in aggs:
                return self._create_dataframe_from_terms_aggregations(data)
            elif 'date_histogram' in aggs:
                return self._create_dataframe_from_date_histogram_aggregations(data)
            elif 'aggs' in aggs:
                return self._create_dataframe_from_complex_aggregations(data)
            else:
                raise ValueError("Unsupported aggregation type")
        elif "fields" in data[0] and isinstance(data[0]["fields"], dict):
            return self._create_dataframe_from_fields(data)
        else:
            raise ValueError("Unrecognized data format in the response.")

    def _create_dataframe_from_hits(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los hits.
        """
        all_fields = [hit['fields'] for hit in data]
        return pd.DataFrame(all_fields)

    def _create_dataframe_from_terms_aggregations(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los resultados de las agregaciones de términos.
        """
        aggs_key = list(self._query['aggs'].keys())[0]
        field_name = self._query['aggs'][aggs_key]['terms']['field']
        
        # Extraer solo el nombre del campo sin el prefijo del índice (si existe)
        field_name = field_name.split('.')[-1]
        
        df = pd.DataFrame(data)
        df.rename(columns={"key": field_name, "doc_count": "count"}, inplace=True)
        return df

    def _create_dataframe_from_date_histogram_aggregations(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los resultados de las agregaciones de histograma de fechas.
        """
        df = pd.DataFrame(data)
        df.rename(columns={"key_as_string": "date", "doc_count": "count"}, inplace=True)
        return df

    def _create_dataframe_from_complex_aggregations(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los resultados de las agregaciones complejas.
        """
        df = pd.DataFrame(data)
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renombra las columnas del DataFrame basadas en los nombres de los campos de las sub-agregaciones en la consulta.
        """
        aggs_key = list(self._query['aggs'].keys())[0]
        sub_aggs = self._query['aggs'][aggs_key]['aggs']

        # Crear un diccionario para el mapeo de nombres
        column_mapping = {}
        for sub_agg_key, sub_agg in sub_aggs.items():
            if 'field' in sub_agg:
                field_name = sub_agg['field'].split('.')[-1]
                column_mapping[sub_agg_key] = field_name

        # Renombrar las columnas
        df.rename(columns=column_mapping, inplace=True)
        return df

    def _create_dataframe_from_fields(self, data) -> pd.DataFrame:
        """
        Crea un DataFrame de pandas a partir de los campos extraídos.
        """
        fields = self._extract_fields(data)
        df = pd.DataFrame(fields)
        df = df.apply(lambda col: col.map(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x))
        return df

    def _extract_fields(self, response):
        """
        Extrae los campos de la respuesta y los estandariza.
        """
        all_fields = [hit['fields'] for hit in response]
        all_keys = set(key for fields in all_fields for key in fields)
        standardized_fields = [{key: fields.get(key, [None]) for key in all_keys} for fields in all_fields]
        return standardized_fields

    def _normalize_array_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza los valores que vienen como arrays a valores simples si solo tienen un elemento.
        """
        for col in df.columns:
            df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)
        return df

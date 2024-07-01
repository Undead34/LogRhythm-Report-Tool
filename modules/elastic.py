import os
import ast
import glob
import json
import pandas as pd
from datetime import datetime
from elasticsearch import Elasticsearch


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
    
    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        self._date_range = (start_date, end_date)

    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self._entity_ids = entity_ids

    def load_queries(self, folder: str) -> list['Package']:
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
            print(f"Error al procesar el archivo {file}: {e}")
            return {}

    def _is_valid_data(self, data: dict) -> bool:
        return 'query' in data and 'query' in data['query'] and 'type' in data

    def _process_query_by_type(self, data: dict, date_range: dict) -> dict:
        if data['type'] == "1":
            return self._replace_placeholders_type_1(data, date_range)
        elif data['type'] == "2":
            return self._replace_placeholders_type_2(data, date_range)
        elif data['type'] == "3":
            return self._replace_placeholders_type_3(data, date_range)
        elif data['type'] == "4":
            return self._replace_placeholders_type_4(data, date_range)
        else:
            raise ValueError(f"Tipo de datos no reconocido: {data['type']}")

    def _replace_placeholders_type_1(self, data: dict, date_range: dict) -> dict:
        query_str = json.dumps(data['query'])
        query_str = query_str.replace('{{gte}}', str(date_range['gte'])).replace('{{lte}}', str(date_range['lte']))

        entity_id_matches = [{'match': {'entityId': str(id)}} for id in self._entity_ids['EntityID']]
        entity_id_placeholder = r'[{"match": {"entityId": "{{entity_ids}}"}}]'
        query_str = query_str.replace(entity_id_placeholder, json.dumps(entity_id_matches))

        return self._load_json_str(query_str)

    def _replace_placeholders_type_2(self, data: dict, date_range: dict) -> dict:
        query_str = json.dumps(data['query'])
        query_str = query_str.replace('{{gte}}', str(date_range['gte'])).replace('{{lte}}', str(date_range['lte']))

        entity_ids_str = " || ".join([str(id) for id in self._entity_ids['EntityID']])
        query_str = query_str.replace('{{entity_ids}}', f'entityId: ({entity_ids_str})')

        return self._load_json_str(query_str)

    def _replace_placeholders_type_3(self, data: dict, date_range: dict) -> dict:
        query_str = json.dumps(data['query'])
        query_str = query_str.replace('{{gte}}', str(date_range['gte'])).replace('{{lte}}', str(date_range['lte']))

        entity_ids_str = " OR ".join([str(id) for id in self._entity_ids['EntityID']])
        query_str = query_str.replace('{{entity_ids}}', f'entityId: ({entity_ids_str})')

        return self._load_json_str(query_str)

    def _replace_placeholders_type_4(self, data: dict, date_range: dict) -> dict:
        query_str = json.dumps(data['query'])
        query_str = query_str.replace('{{gte}}', str(date_range['gte'])).replace('{{lte}}', str(date_range['lte']))

        entity_ids_str = " AND ".join([f"entityId:{id}" for id in self._entity_ids['EntityID']])
        query_str = query_str.replace('{{entity_ids}}', entity_ids_str)

        return self._load_json_str(query_str)

    def _load_json_str(self, json_str: str) -> dict:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            print("Query string con error:", json_str)
            raise

class Package:
    def __init__(self, elastic: 'Elastic', data: dict) -> None:
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
        try:
            self._validate_query_parameters()
            index_str = ",".join(self._index) if isinstance(self._index, list) else self._index
            response = self._execute_query(index_str)
            if response is None:
                raise ValueError("No data found in the response.")

            if self._type == "1":
                df = self._handle_type_1(response)
            elif self._type == "2":
                df = self._handle_type_2(response)
            elif self._type == "3":
                df = self._handle_type_3(response)
            elif self._type == "4":
                df = self._handle_type_4(response)
            else:
                raise ValueError(f"Tipo de datos no reconocido: {self._type}")

            df = self._normalize_array_values(df)
            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
    
    def _validate_query_parameters(self):
        if not self._id or not self._index or not self._query:
            raise ValueError("ID, index, and query must be provided.")

    def _execute_query(self, index_str: str):
        return self._es.msearch(index=index_str, body=self._query, _source=True) if self._mode == "multi" else self._es.search(index=index_str, body=self._query, _source=True)

    def _handle_type_1(self, response):
        hits = self._extract_hits(response)
        if hits:
            df_hits = self._create_dataframe_from_hits(hits)
        else:
            df_hits = pd.DataFrame()

        aggregations = self._extract_aggregations(response)
        if aggregations:
            df_aggs = self._create_dataframe(aggregations)
        else:
            df_aggs = pd.DataFrame()

        df = pd.concat([df_hits, df_aggs], axis=1) if not df_hits.empty and not df_aggs.empty else df_hits if not df_hits.empty else df_aggs
        return df

    def _handle_type_2(self, response):
        aggregations = self._extract_aggregations(response)
        if aggregations:
            df_aggs = self._create_dataframe(aggregations)
            df_aggs = self._rename_columns(df_aggs)
        else:
            df_aggs = pd.DataFrame()
        return df_aggs

    def _handle_type_3(self, response):
        print(len(response["aggregations"]["top_origin_ips"]["buckets"]))  # Añade esta línea para imprimir la respuesta completa
        aggregations = self._extract_aggregations(response)
        if aggregations:
            df_aggs = self._create_dataframe(aggregations)
            if 'top_hits' in self._query['aggs'][list(self._query['aggs'].keys())[0]]['aggs']:
                df_aggs = self._expand_top_hits(df_aggs, 'top_hits')
            df_aggs = self._rename_columns(df_aggs)
        else:
            df_aggs = pd.DataFrame()

        return df_aggs

    def _handle_type_4(self, response):
        aggregations = self._extract_aggregations(response)
        
        if aggregations:
            df_aggs = self._create_dataframe_from_date_histogram_aggregations(aggregations)
        else:
            df_aggs = pd.DataFrame()
        return df_aggs

    def _extract_hits(self, response):
        if "responses" in response:
            hits = []
            for res in response["responses"]:
                hits.extend(res.get("hits", {}).get("hits", []))
            return hits
        else:
            return response.get("hits", {}).get("hits", [])

    def _extract_aggregations(self, response):
        aggregations = response.get("aggregations", {})
        if not aggregations:
            return []

        aggs_key = list(self._query['aggs'].keys())[0]
        aggs = self._query['aggs'][aggs_key]

        if 'terms' in aggs:
            return aggregations.get(aggs_key, {}).get("buckets", [])
        elif 'date_histogram' in aggs:
            return aggregations.get(aggs_key, {}).get("buckets", [])
        elif 'aggs' in aggs:
            return aggregations.get(aggs_key, {}).get("buckets", [])
        else:
            raise ValueError("Unsupported aggregation type")

    def _create_dataframe(self, data) -> pd.DataFrame:
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
        all_fields = [hit['_source'] for hit in data]
        return pd.DataFrame(all_fields)

    def _create_dataframe_from_terms_aggregations(self, data) -> pd.DataFrame:
        aggs_key = list(self._query['aggs'].keys())[0]
        field_name = self._query['aggs'][aggs_key]['terms']['field'].split('.')[-1]
        df = pd.DataFrame(data)
        df.rename(columns={"key": field_name, "doc_count": "count"}, inplace=True)
        return df

    def _create_dataframe_from_date_histogram_aggregations(self, data) -> pd.DataFrame:
        df = pd.DataFrame(data)
        df.rename(columns={"key_as_string": "date", "doc_count": "count"}, inplace=True)
        return df

    def _create_dataframe_from_complex_aggregations(self, data) -> pd.DataFrame:
        return pd.DataFrame(data)

    def _expand_top_hits(self, df: pd.DataFrame, top_hits_field: str) -> pd.DataFrame:
        def extract_top_hits_data(row):
            hits = row[top_hits_field]['hits']['hits']
            if hits:
                hit_data = hits[0]['fields']
                for key, value in hit_data.items():
                    row[key] = value[0] if isinstance(value, list) and len(value) == 1 else value
            return row

        return df.apply(extract_top_hits_data, axis=1).drop(columns=[top_hits_field])

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        aggs_key = list(self._query['aggs'].keys())[0]
        sub_aggs = self._query['aggs'][aggs_key]['aggs']

        # Crear un diccionario para el mapeo de nombres
        column_mapping = {}
        for sub_agg_key, sub_agg in sub_aggs.items():
            # Aquí es donde necesitas agregar una capa adicional de indización
            for _, agg_content in sub_agg.items():
                if 'field' in agg_content:
                    field_name = agg_content['field'].split('.')[-1]
                    column_mapping[sub_agg_key] = field_name

        # Renombrar las columnas
        df.rename(columns=column_mapping, inplace=True)

        return df

    def _create_dataframe_from_fields(self, data) -> pd.DataFrame:
        fields = self._extract_fields(data)
        df = pd.DataFrame(fields)
        df = df.apply(lambda col: col.map(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x))
        return df

    def _extract_fields(self, response):
        all_fields = [hit['fields'] for hit in response]
        all_keys = set(key for fields in all_fields for key in fields)
        standardized_fields = [{key: fields.get(key, [None]) for key in all_keys} for fields in all_fields]
        return standardized_fields

    def _extract_aggregations(self, response):
        aggregations = response.get("aggregations", {})
        if not aggregations:
            return []

        aggs_key = list(self._query['aggs'].keys())[0]
        return aggregations.get(aggs_key, {}).get("buckets", [])

    def _create_dataframe_from_date_histogram_aggregations(self, data) -> pd.DataFrame:
        if not data:
            return pd.DataFrame()
        # Convertir los buckets en un DataFrame
        df = pd.DataFrame(data)
        if not df.empty:
            df.rename(columns={"key_as_string": "date", "key": "epoch_millis", "doc_count": "count"}, inplace=True)
        return df

    def _normalize_array_values(self, df: pd.DataFrame) -> pd.DataFrame:
        # Normaliza los valores que vienen como arrays a valores simples si solo tienen un elemento
        df = df.apply(lambda x: x.map(lambda y: y[0] if isinstance(y, list) and len(y) == 1 else y))
        
        # Renombrar columnas duplicadas
        df.columns = self._rename_duplicate_columns(list(df.columns))
        
        df = df.apply(lambda x: x.map(self._deserialize))
        
        # Aplicar lambda para extraer el valor de los diccionarios si existen
        df = df.apply(lambda x: x.map(lambda y: y['value'] if isinstance(y, dict) and 'value' in y else y))
        
        return df

    def _rename_duplicate_columns(self, columns):
        seen = {}
        for i, col in enumerate(columns):
            if col in seen:
                seen[col] += 1
                columns[i] = f"{col}_{seen[col]}"
            else: seen[col] = 0
        return columns

    def _deserialize(self, x):
        if isinstance(x, str):
            try:
                return ast.literal_eval(x)
            except (ValueError, SyntaxError):
                return x
        return x
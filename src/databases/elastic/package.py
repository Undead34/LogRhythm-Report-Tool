import ast
import json
import pandas as pd
from src.utils.logger import get_logger
from typing import TYPE_CHECKING, Union, Dict, Any

if TYPE_CHECKING:
    from . import Elastic

class Package:
    def __init__(self, elastic: 'Elastic', data: dict) -> None:
        self._initialize_attributes(elastic, data)
        self.logger = get_logger()

    def _initialize_attributes(self, elastic, data):
        self._es = elastic._es
        self._id = data.get("id")
        self._metadata = data.get("metadata", {})
        self._name = self._metadata.get("name")
        self._description = self._metadata.get("description")
        self._processing_policy = data.get("processing_policy", {})
        self._mode = self._processing_policy.get("mode")
        self._index = self._processing_policy.get("index")
        self._query = data.get("query")
        self._result_processing = data.get("result_processing", {})
        self._include_totals = self._result_processing.get("include_totals", False)
        self._columns = self._result_processing.get("columns", [])

    def run(self) -> pd.DataFrame:
        try:
            self._validate_query_parameters()
            index_str = self._format_index()
            response = self._execute_query(index_str)

            if not response:
                raise ValueError("No data found in the response.")

            df = self._process_response(response)
            df = self._normalize_array_values(df)

            return df

        except Exception as e:
            self.logger.error(f"An error has occurred: {e}")
            raise

    def _validate_query_parameters(self):
        if not all([self._id, self._index, self._query]):
            raise ValueError("ID, index, and query must be provided.")

    def _format_index(self) -> str:
        return ",".join(self._index) if isinstance(self._index, list) else self._index

    def _execute_query(self, index_str: str) -> Dict[str, Any]:
        query_func = self._es.msearch if self._mode == "multi" else self._es.search
        return query_func(index=index_str, body=self._query, _source=True)

    def _process_response(self, response: dict) -> pd.DataFrame:
        if "aggregations" in response:
            return self._process_aggregations(response["aggregations"])
        if "hits" in response:
            return self._handle_hits(response["hits"])
        raise ValueError("Unknown response format.")

    def _process_aggregations(self, aggregations: dict) -> pd.DataFrame:
        if self._is_type_1_aggregation(aggregations):
            return self._handle_type_1_aggregations(aggregations)
        if self._is_type_3_aggregation(aggregations):
            return self._handle_type_3_aggregations(aggregations)
        return self._handle_type_2_aggregations(aggregations)

    def _is_type_1_aggregation(self, aggregations: dict) -> bool:
        return any(
            'buckets' in agg and any(self._find_top_hits_key(bucket) for bucket in agg['buckets'])
            for agg in aggregations.values()
        )

    def _is_type_3_aggregation(self, aggregations: dict) -> bool:
        return any(
            'buckets' in agg and any('date_histogram' in bucket for bucket in agg['buckets'])
            for agg in aggregations.values()
        )

    def _find_top_hits_key(self, bucket: dict) -> Union[str, None]:
        for key, value in bucket.items():
            if isinstance(value, dict) and 'hits' in value.get('hits', {}):
                return key
        return None

    def _handle_type_1_aggregations(self, aggregations: dict) -> pd.DataFrame:
        all_hits = [
            hit
            for agg in aggregations.values() if 'buckets' in agg
            for bucket in agg['buckets']
            if (top_hits_key := self._find_top_hits_key(bucket))
            for hit in self._extract_hits(bucket[top_hits_key]['hits']['hits'])
        ]
        return self._create_dataframe(all_hits, aggregations)

    def _handle_type_2_aggregations(self, aggregations: dict) -> pd.DataFrame:
        all_hits = [
            bucket
            for agg in aggregations.values() if 'buckets' in agg
            for bucket in agg['buckets']
        ]
        return self._create_dataframe(all_hits, aggregations)

    def _handle_type_3_aggregations(self, aggregations: dict) -> pd.DataFrame:
        df = self._handle_type_2_aggregations(aggregations)
        if df.empty:
            return pd.DataFrame()

        expanded_histograms = [
            self._expand_histogram(row)
            for _, row in df.iterrows()
            if 'date_histogram' in row and row['date_histogram']
        ]

        combined_df = pd.concat(expanded_histograms, ignore_index=True)
        return combined_df[['key_as_string', 'key', 'doc_count']]

    def _expand_histogram(self, row: pd.Series) -> pd.DataFrame:
        hist_df = pd.DataFrame(row['date_histogram']['buckets'])
        hist_df['key'] = row['key']
        hist_df['doc_count'] = row['doc_count']
        return hist_df

    def _handle_hits(self, hits: dict) -> pd.DataFrame:
        if not hits["hits"]:
            df = pd.DataFrame()
        else:
            all_fields = [
                {**hit.get('_source', {}), **hit.get('fields', {})}
                for hit in hits["hits"]
            ]
            df = pd.DataFrame(all_fields)
        
        if self._include_totals:
            total_key = next((col.get('_include_totals') for col in self._columns if '_include_totals' in col), None)
            total_value = hits.get("total", 0)
            
            if total_key and total_value:
                total_df = pd.DataFrame([{total_key: total_value}])
                df = pd.concat([df, total_df], axis=1)

        return df

    def _extract_hits(self, hits: list) -> list:
        return [{**hit.get('_source', {}), **hit.get('fields', {})} for hit in hits]

    def _create_dataframe(self, all_hits: list, source: dict) -> pd.DataFrame:
        df = pd.DataFrame(all_hits)
        if self._include_totals:
            df = self._add_totals(df, source)
        return df

    def _add_totals(self, df: pd.DataFrame, source: dict) -> pd.DataFrame:
        total_key = next((col.get('_include_totals') for col in self._columns if '_include_totals' in col), None)
        total_value = source.get("hits", {}).get("total", 0)
        if total_key and total_value:
            total_df = pd.DataFrame([{total_key: total_value}])
            df = pd.concat([df, total_df], axis=1)
        return df

    def _normalize_array_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.apply(lambda col: col.map(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x))
        df.columns = self._rename_duplicate_columns(df.columns)
        df = df.apply(lambda col: col.map(self._deserialize))
        return df.apply(lambda col: col.map(lambda x: x['value'] if isinstance(x, dict) and 'value' in x else x))

    def _rename_duplicate_columns(self, columns: pd.Index) -> pd.Index:
        seen = {}
        new_columns = []
        for col in columns:
            if col in seen:
                seen[col] += 1
                new_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_columns.append(col)
        return pd.Index(new_columns)

    def _deserialize(self, x: Any) -> Any:
        if isinstance(x, str):
            try:
                return ast.literal_eval(x)
            except (ValueError, SyntaxError):
                pass
        return x

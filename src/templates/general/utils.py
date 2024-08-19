import calendar
import pandas as pd

def get_human_readable_period(start_date, end_date):
    month_translation = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril', 
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto', 
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    start_month = calendar.month_name[start_date.month]
    end_month = calendar.month_name[end_date.month]
    start_month_es = month_translation[start_month]
    end_month_es = month_translation[end_month]
    start_date_str = start_date.strftime(f'%d de {start_month_es} de %Y')
    end_date_str = end_date.strftime(f'%d de {end_month_es} de %Y')
    
    return start_date_str, end_date_str


def aux_parse_12(data: pd.DataFrame) -> pd.DataFrame:
        def parse_msgclassname_counts(msgclassname_counts_dict):
            try:
                return msgclassname_counts_dict["buckets"]
            except (KeyError, TypeError) as e:
                print(f"Error parsing: {msgclassname_counts_dict}\nError: {e}")
                return []
        data["parsed_counts"] = data["msgclassname_counts"].apply(parse_msgclassname_counts)
        msgclassname_expanded = data["parsed_counts"].explode().apply(pd.Series)
        msgclassname_expanded["msgsourcetypename"] = data["key"].repeat(msgclassname_expanded.groupby(level=0).size().values)
        msgclassname_expanded["total_doc_count"] = data["doc_count"].repeat(msgclassname_expanded.groupby(level=0).size().values)
        msgclassname_expanded.rename(columns={"key": "msgclassname", "doc_count": "msg_doc_count"}, inplace=True)
        msgclassname_expanded.reset_index(drop=True, inplace=True)

        return msgclassname_expanded
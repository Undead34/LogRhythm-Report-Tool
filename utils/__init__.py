from datetime import datetime
import pandas as pd
import uuid
import os


class ElementList(list):
    def __iadd__(self, other):
        if not isinstance(other, list):
            other = [other]
        return super().__iadd__(other)

def get_file_name(output_path: str, f: str, s: dict) -> str:
    options = {
        "ltime": datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        "stime": datetime.now().strftime('%Y-%m-%d'),
        "uuid": uuid.uuid4(),
        **s
    }

    filename = f.format(**options)

    return os.path.realpath(os.path.join(output_path, f"{filename}.pdf"))


def execute_callbacks(selected_tables: pd.DataFrame):
    outputs = []
    for index, row in selected_tables.iterrows():
        callback = row['Callback']
        if callable(callback):
            result = callback()
            outputs.append(result)
    return outputs


def clear_console():
    # Limpiar la consola dependiendo del sistema operativo
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # MacOS, Linux
        os.system('clear')
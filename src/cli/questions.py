from datetime import time, datetime
import pandas as pd
import questionary
import sys
import os

from .date_selector import DateSelector
from .list_reorder import ListReorder

def select_entities(entities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples entidades desde un DataFrame.
    """
    try:
        entities = entities_df[['EntityID', 'FullName']]
        choices = [{"name": row['FullName'], "value": row['EntityID']} for _, row in entities.iterrows()]
        answers = questionary.checkbox(
            "Seleccionar las entidades que se incluirán en el reporte: ",
            choices=choices,
            instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)").ask()

        if not answers:
            print("No se seleccionaron entidades. Saliendo...")
            sys.exit(0)

        selected_entities = entities[entities['EntityID'].isin(answers)].reset_index(drop=True)
        return selected_entities
    except Exception as e:
        print("Error al seleccionar entidades:", e)
        sys.exit(1)


def customize_signature(default_signature: dict) -> dict:
    """
    Obtiene la firma del reporte desde el usuario, con valores predeterminados.
    """
    questions = [
        {"type": "input", "name": "title", "message": "Ingrese el título del reporte:", "default": default_signature.get("title", "")},
        {"type": "input", "name": "author", "message": "Ingrese el autor del reporte:", "default": default_signature.get("author", "Netready Solutions")},
        {"type": "input", "name": "subject", "message": "Ingrese el asunto del reporte:", "default": default_signature.get("subject", "Netready Solutions - LogRhythm")},
        {"type": "input", "name": "keywords", "message": "Ingrese las palabras clave del reporte (separadas por comas):", "default": ", ".join(default_signature.get("keywords", ["LogRhythm", "Netready Solutions", "Report", "Confidential"]))}
    ]

    answers = questionary.prompt(questions)
    answers["keywords"] = [keyword.strip() for keyword in answers["keywords"].split(",")]
    answers["producer"] = default_signature.get("producer", "LogRhythm Report Tool - github.com/Undead34")
    answers["creator"] = default_signature.get("creator", "@Undead34")
    return answers


def confirm_template_usage() -> bool:
    """
    Pregunta al usuario si desea seleccionar una plantilla de reporte.
    """
    return questionary.confirm("¿Desea seleccionar una plantilla de reporte?").ask()


def get_output_details() -> tuple:
    """
    Obtiene los detalles de salida del reporte desde el usuario.
    """
    questions = [
        {"type": "input", "name": "output_path", "message": "Ingrese la ruta del directorio de salida (predeterminada: ./output):", "default": "./output"},
        {"type": "input", "name": "filename_format", "message": "Ingrese el formato del nombre del archivo (e.g., {client_name}, {title}, {stime}, {ltime}, {author}, {subject}, {uuid}):", "default": "{client_name} - {stime}"}
    ]

    answers = questionary.prompt(questions)
    output_path = answers["output_path"]
    filename_format = answers["filename_format"]

    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except OSError as e:
            print(f"Error al crear el directorio: {e}")
            sys.exit(1)

    return output_path, filename_format


def get_client_details() -> tuple:
    """
    Obtiene los detalles del cliente desde el usuario.
    """
    client_name_response = questionary.prompt({
        "type": "input", "name": "client_name", "message": "Ingrese el nombre del cliente (predeterminada: Cliente):", "default": "Cliente"
    })

    client_name = client_name_response.get('client_name', 'Cliente')
    default_logo_path = f"./assets/images/clients/{client_name.lower()}/logo.png"

    client_logo_response = questionary.prompt({
        "type": "input", "name": "client_logo", "message": "Ingrese la ruta al logo para el reporte: (e.g: ./assets/images/clients/cliente/logo.png)", "default": default_logo_path
    })

    client_logo = client_logo_response.get('client_logo', default_logo_path)

    if not os.path.exists(client_logo):
        print(f"El archivo no existe: {client_logo}")
        sys.exit(1)

    if os.path.isdir(client_logo):
        print(f"Error: la ruta no puede ser un directorio")
        sys.exit(1)

    return client_name, client_logo


def select_tables(tables_df: pd.DataFrame) -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples tablas para incluir en el reporte.
    """
    choices = [{"name": row['Name'], "value": row['Callback']} for index, row in tables_df.iterrows()]
    answers = questionary.checkbox(
        "Seleccionar las tablas que se incluirán en el reporte: ",
        choices=choices,
        instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)").ask()

    if not answers:
        print("No se seleccionaron tablas.")
        return pd.DataFrame()

    selected_tables = tables_df[tables_df['Callback'].isin(answers)].reset_index(drop=True)
    return selected_tables


def select_charts(charts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples gráficos para incluir en el reporte.
    """
    choices = [{"name": row['Name'], "value": row['Callback']} for index, row in charts_df.iterrows()]
    answers = questionary.checkbox(
        "Seleccionar los gráficos que se incluirán en el reporte: ",
        choices=choices,
        instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)").ask()

    if not answers:
        print("No se seleccionaron gráficos.")
        return pd.DataFrame()

    selected_charts = charts_df[charts_df['Callback'].isin(answers)].reset_index(drop=True)
    return selected_charts


def select_date_range() -> tuple[datetime, datetime]:
    """
    Permite al usuario seleccionar un rango de fechas.
    """
    selector = DateSelector(
        message="Seleccione una fecha", 
        enter_year_prompt="Introduzca el año: ", 
        selected_date_message="Fecha seleccionada: {date}",
        instructions={
            'navigation': "Bienvenido a «LogRhythm Report Tool», para crear su reporte primero tenemos que configurar algunas cosas.\nUtilice las flechas del teclado «↑↓←→» para navegar, «ENTER» para seleccionar la fecha",
            'change_year': "Pulse «y» para cambiar el año y «ENTER» para confirmar."
        }
    )

    start_date = selector.select_date()
    end_date = selector.select_date()

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    return (start_datetime, end_datetime)

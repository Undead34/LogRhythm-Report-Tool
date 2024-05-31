import questionary
import pandas as pd
import os
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import MSQLServer


def select_entities(db: 'MSQLServer') -> pd.DataFrame:
    try:
        entities = db.get_entities().get(['EntityID', 'FullName'])

        # Crear una lista de opciones a partir del DataFrame
        choices = [{"name": row['FullName'], "value": row['EntityID']}
                   for index, row in entities.iterrows()]

        # Preguntar al usuario para seleccionar múltiples entidades
        answers = questionary.checkbox(
            "Seleccionar las entidades que se incluirán en el reporte: ",
            choices=choices,
            instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)",
        ).ask()

        if answers == None or len(answers) == 0:
            print("Saliendo...")
            sys.exit(0)

        # Filtrar el DataFrame para obtener las entidades seleccionadas
        selected_entities = entities[entities['EntityID'].isin(
            answers)].reset_index()

        return selected_entities
    except Exception as e:
        print("Error weon", e)


def get_signature(default_signature: dict) -> dict:
    questions = [
        {
            "type": "input",
            "name": "title",
            "message": "Ingrese el título del reporte:",
            "default": default_signature.get("title", "")
        },
        {
            "type": "input",
            "name": "author",
            "message": "Ingrese el autor del reporte:",
            "default": default_signature.get("author", "Netready Solutions")
        },
        {
            "type": "input",
            "name": "subject",
            "message": "Ingrese el asunto del reporte:",
            "default": default_signature.get("subject", "Netready Solutions - LogRhythm")
        },
        {
            "type": "input",
            "name": "keywords",
            "message": "Ingrese las palabras clave del reporte (separadas por comas):",
            "default": ", ".join(default_signature.get("keywords", ["LogRhythm", "Netready Solutions", "Report", "Confidential"]))
        }
    ]

    answers = questionary.prompt(questions)

    # Convertir las palabras clave de string a lista
    answers["keywords"] = [keyword.strip()
                           for keyword in answers["keywords"].split(",")]

    # Agregar los campos inmutables
    answers["producer"] = default_signature.get(
        "producer", "LogRhythm Report Tool - github.com/Undead34")
    answers["creator"] = default_signature.get("creator", "@Undead34")

    return answers


def get_output_details() -> tuple:
    questions = [
        {
            "type": "input",
            "name": "output_path",
            "message": "Ingrese la ruta del directorio de salida (predeterminada: ./output):",
            "default": "./output"
        },
        {
            "type": "input",
            "name": "filename_format",
            "message": "Ingrese el formato del nombre del archivo (e.g., {client_name}, {title}, {stime}, {ltime}, {author}, {subject}):",
            "default": "{client_name} - {stime}"
        }
    ]

    answers = questionary.prompt(questions)

    output_path = answers["output_path"]
    filename_format = answers["filename_format"]

    # Validar la ruta de salida
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except OSError as e:
            print(f"Error al crear el directorio: {e}")
            sys.exit(1)

    return output_path, filename_format


def get_client_details() -> tuple:
    client_name_response = questionary.prompt({
        "type": "input",
        "name": "client_name",
        "message": "Ingrese el nombre del cliente (predeterminada: Cliente):",
        "default": "Cliente"
    })

    client_name = client_name_response.get('client_name', 'Cliente')

    # Formatear la ruta del logo usando el nombre del cliente
    default_logo_path = f"./assets/images/clients/{client_name.lower()}/logo.png"

    client_logo_response = questionary.prompt({
        "type": "input",
        "name": "client_logo",
        "message": "Ingrese la ruta al logo para el reporte: (e.g: ./assets/images/clients/cliente/logo.png)",
        "default": default_logo_path
    })

    client_logo = client_logo_response.get('client_logo', default_logo_path)

    # Validar la ruta de salida
    if not os.path.exists(client_logo):
        print(f"El archivo no existe: {client_logo}")
        sys.exit(1)

    if os.path.isdir(client_logo):
        print(f"Error: la ruta no puede ser un directorio")
        sys.exit(1)

    return (client_name, client_logo)


def select_tables(tables: pd.DataFrame):
    # Crear una lista de opciones a partir del DataFrame
    choices = [{"name": row['TableName'], "value": row['TableCallback']}
               for index, row in tables.iterrows()]

    # Preguntar al usuario para seleccionar múltiples entidades
    answers = questionary.checkbox(
        "Seleccionar las tablas que se incluirán en el reporte: ",
        choices=choices,
        instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)",
    ).ask()

    if not answers:
        print("No se seleccionaron tablas.")
        return pd.DataFrame()

    # Filtrar el DataFrame para obtener las entidades seleccionadas
    selected_tables = tables[tables['TableCallback'].isin(
        answers)].reset_index(drop=True)

    return selected_tables

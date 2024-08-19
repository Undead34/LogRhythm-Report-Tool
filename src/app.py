from datetime import datetime
import pandas as pd
import json

from .cli.questions import (
    select_entities,
    select_date_range,
    customize_signature,
    get_client_details,
    get_output_details,
)

from src.databases import MSQLServer, Elastic

from .reports import skeleton
from .templates import Templates

from .utils.constants import DEFAULT_SIGNATURE
from .utils import get_file_name
from .utils.logger import get_logger

class Config:
    date_range: tuple[datetime, datetime]
    entities: pd.DataFrame
    client_details: tuple[str, str]
    output_file: str
    signature: dict

    @staticmethod
    def default() -> 'Config':
        config = Config()

        # Modo debug: usar valores predefinidos
        start, end = datetime(2024, 7, 1), datetime(2024, 7, 31)
        entities = pd.DataFrame(data={'EntityID': [4], 'FullName': ['Farmatodo']})
        signature = DEFAULT_SIGNATURE.copy()
        client_name, client_logo = 'Farmatodo', './assets/images/clients/farmatodo/logo.png'
        signature["client_name"] = client_name
        output_path, filename_format = "./output", "{client_name} - {stime}"
        output_file = get_file_name(output_path, filename_format, signature)
        
        # Asignar valores a config
        config.date_range = (start, end)
        config.entities = entities
        config.client_details = (client_name, client_logo)
        signature["client_logo"] = client_logo
        config.signature = signature
        config.output_file = output_file

        return config

def run_interactive_mode(args) -> Config:
    logger = get_logger()
    
    config = Config()

    # Selección de rango de fechas
    start, end = select_date_range()
    config.date_range = (start, end)
    logger.debug("Rango de fechas seleccionado: %s - %s", start, end)

    print("\nRango de fechas seleccionado:")
    print(f"Desde {start.strftime('%Y-%m-%dT%H:%M:%SZ')} hasta {end.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    
    # Selección de entidades
    logger.info("Seleccionando entidades...")
    config.entities = select_entities(MSQLServer.get_entities())
    logger.debug("Entidades seleccionadas: %s", config.entities)

    print("\nEntidades seleccionadas:")
    print(config.entities)
    
    # Configuración de firma y detalles del cliente
    logger.info("Obteniendo detalles del cliente y configurando la firma...")
    signature = customize_signature(DEFAULT_SIGNATURE)
    client_name, client_logo = get_client_details()
    config.client_details = (client_name, client_logo)
    
    signature["client_name"] = client_name
    signature["client_logo"] = client_logo

    logger.debug("Detalles del cliente: nombre=%s, logo=%s", client_name, client_logo)
    logger.debug("Firma configurada: %s", signature)

    # Detalles del archivo de salida
    logger.info("Obteniendo detalles del archivo de salida...")
    output_path, filename_format = get_output_details()
    config.output_file = get_file_name(output_path, filename_format, signature)
    config.signature = signature

    logger.debug("Ruta del archivo de salida: %s", config.output_file)

    print("\nDetalles de configuración:")
    print(f"Cliente: {config.client_details[0]}")
    print(f"Logo del cliente: {config.client_details[1]}")
    print(f"Archivo de salida: {config.output_file}")

    # Aquí podrías incluir cualquier lógica adicional que necesite tu flujo interactivo
    logger.info("Configuración completa. Listo para proceder con el flujo principal.")

    return config

def run_main_program(args, config: Config):
    logger = get_logger()

    logger.info("Iniciando el flujo principal del programa...")

    # Inicialización de Elastic y MSQLServer
    logger.info("Inicializando Elastic y MSQLServer...")
    elastic = Elastic()
    database = MSQLServer()

    # Establecer el rango de fechas en las instancias de Elastic y MSQLServer
    start, end = config.date_range
    logger.debug("Estableciendo el rango de fechas: %s - %s", start, end)
    elastic.set_date_range(start, end)
    database.set_date_range(start, end)

    # Establecer las entidades seleccionadas en la base de datos
    entities = config.entities
    logger.debug("Estableciendo las entidades seleccionadas en Elastic y MSQLServer...")
    database.set_entity_ids(entities)
    elastic.set_entity_ids(entities)

    # Cargar las consultas desde un archivo
    logger.info("Cargando las consultas desde el archivo...")
    queries = elastic.load_queries("./querys/elastic")
    
    if args.export:
        elastic.export_to_csv("./querys/elastic", "./output/csv")
        database.export_to_csv("./output/csv")

    signature = config.signature

    logger.debug("Firma configurada: %s", json.dumps(signature, indent=2))

    # Generate Report
    logger.info("Generando el reporte...")

    report = skeleton.Report(config.output_file)
    templates = Templates(report, queries, database, signature, config)

    report.load_template(templates.get_template("general"))

    report.build()
    print("✅ [Reporte generado]\nRuta de salida del archivo:", config.output_file)

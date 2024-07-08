#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from src.cli import parse_arguments
from src.utils.logger import configure_logger, logging
from src.app import run_interactive_mode, run_main_program, Config

# Verificar si la versión de Python es 3.10 o superior
if sys.version_info < (3, 10):
    print("LogRhythm Report Tool requires Python 3.10 or higher.")
    sys.exit(1)

def main():
    # sys.argv.append("-dv")

    args = parse_arguments()
    logger = configure_logger(args.debug, args.verbose)

    # Configuración por defecto (modo debug)
    config = Config.default()

    # Modo interactivo
    if args.interactive:
        try:
            logger.info("Iniciando modo interactivo...")
            config = run_interactive_mode(args)
        except Exception as e:
            logger.error("Error en el modo interactivo: %s", e)
            sys.exit(1)

    # Ejecución del flujo principal
    try:
        logger.info("Ejecutando el flujo principal del programa...")
        run_main_program(args, config)
    except Exception as e:
        logger.error("Error en el flujo principal del programa: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Interrupción del usuario.")
        sys.exit(0)
    except Exception as e:
        logging.critical("Error inesperado: %s", e)
        sys.exit(1)

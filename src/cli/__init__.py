import argparse, sys

def parse_arguments() -> argparse.Namespace:
    """
    Define y parsea los argumentos de línea de comandos.
    
    :return: Espacio de nombres con los argumentos parseados.
    """
    parser = argparse.ArgumentParser(description="Descripción de tu programa")
    parser.add_argument('-i', '--interactive', action='store_true', help='modo interactivo')
    parser.add_argument('--config-file', type=str, help='ruta al archivo de configuración')
    parser.add_argument('-d', '--debug', action='store_true', help='activar modo debug')
    parser.add_argument('-v', '--verbose', action='store_true', help='activar salida detallada')
    parser.add_argument('-e', '--export', action='store_true', help='activar salida csv')
    
    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()

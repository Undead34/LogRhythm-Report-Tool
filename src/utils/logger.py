import logging

def configure_logger(debug: bool, verbose: bool) -> logging.Logger:
    """
    Configura el logger según los niveles de debug y verbose proporcionados.
    
    :param debug: Activa el nivel de logging DEBUG si es True.
    :param verbose: Activa el nivel de logging INFO si es True.
    :return: Logger configurado.
    """
    logger = logging.getLogger("applogger")
    logger.setLevel(logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING)
    
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    return logger

def get_logger():
    return logging.getLogger("applogger")

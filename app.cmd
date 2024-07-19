@echo off
:: Activa el entorno virtual de Python
call .\.venv\Scripts\activate

:: Ejecuta main.py con todos los argumentos pasados a este script
python main.py %*

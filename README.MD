# LogRhythm Report Tool

LogRhythm Report Tool es una herramienta diseñada para ayudarle a generar reportes de su SIEM LogRhythm desde una interfaz CLI y archivos de configuración de forma automática, personalizable y en formatos PDF y CSV.

## Descripción

LogRhythm Report Tool está escrita en Python y utiliza consultas de Elastic y SQL para recopilar datos, además de metadatos asociados a cada consulta que usted cree o de los valores predeterminados, para determinar qué gráfico o tabla generar.

## Funcionalidades

- **Generación automática de reportes**: Cree reportes personalizados en formato PDF y CSV.
- **Interfaz de línea de comandos (CLI)**: Interactúe con la herramienta desde la consola.
- **Consultas personalizables**: Agregue sus propias consultas en formato JSON y SQL en las carpetas `queries/sql` y `queries/elastic`.
- **Gráficos y tablas**: La herramienta genera gráficos y tablas basados en los metadatos asociados a cada consulta.

## Requisitos

- **Python**: Asegúrese de tener Python instalado en su sistema.
- **Chrome o Chromium Portable**: La herramienta utiliza Selenium para generar gráficos con Chartify y Broke.

## Instalación

1. Clone este repositorio en su máquina local:
    ```bash
    git clone https://github.com/netready/LogRhythm-Report-Tool.git
    ```
2. Navegue al directorio del proyecto:
    ```bash
    cd LogRhythm-Report-Tool
    ```
3. Instale las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. Asegúrese de tener Chrome o Chromium Portable instalado en su sistema.
2. Agregue sus consultas en formato JSON y SQL en las carpetas `queries/sql` y `queries/elastic`. También puede utilizar las consultas que ya se encuentran allí.
3. Ejecute la herramienta desde la línea de comandos:
   python main.py

4. Siga las instrucciones en la pantalla para generar su reporte personalizado.

## Licencia

LogRhythm Report Tool es una herramienta desarrollada por NetReady Solutions y está licenciada bajo la **GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007**. Es de suma importancia que respete esta licencia en caso de crear nuevas consultas o agregar funcionalidades. Sea un buen ser humano y comparta su versión. :D

## Contribuciones

¡Las contribuciones son bienvenidas! Si tiene nuevas consultas o funcionalidades que desea compartir, por favor, abra un issue o envíe un pull request. Nos encantaría ver cómo mejora esta herramienta.

## Contacto

Para preguntas o soporte, por favor contacte a [NetReady Solutions](mailto:soporte@netreadysolutions.com).

---

¡Gracias por usar LogRhythm Report Tool!

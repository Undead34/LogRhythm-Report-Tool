import datetime
import curses
import questionary
import pandas as pd
import os
import sys


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import MSQLServer


def select_entities(db: 'MSQLServer') -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples entidades desde la base de datos.

    Args:
    db (MSQLServer): La conexión a la base de datos.

    Returns:
    pd.DataFrame: DataFrame con las entidades seleccionadas.
    """
    try:
        entities = db.get_entities().get(['EntityID', 'FullName'])

        # Crear una lista de opciones a partir del DataFrame
        choices = [{"name": row['FullName'], "value": row['EntityID']} for _, row in entities.iterrows()]

        # Preguntar al usuario para seleccionar múltiples entidades
        answers = questionary.checkbox(
            "Seleccionar las entidades que se incluirán en el reporte: ",
            choices=choices,
            instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)").ask()

        if not answers:
            print("No se seleccionaron entidades. Saliendo...")
            sys.exit(0)

        # Filtrar el DataFrame para obtener las entidades seleccionadas
        selected_entities = entities[entities['EntityID'].isin(answers)].reset_index(drop=True)

        return selected_entities
    except Exception as e:
        print("Error al seleccionar entidades:", e)
        sys.exit(1)


def get_signature(default_signature: dict) -> dict:
    """
    Obtiene la firma del reporte desde el usuario, con valores predeterminados.

    Args:
    default_signature (dict): Firma predeterminada para el reporte.

    Returns:
    dict: Firma personalizada del reporte.
    """
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
    answers["producer"] = default_signature.get("producer", "LogRhythm Report Tool - github.com/Undead34")
    answers["creator"] = default_signature.get("creator", "@Undead34")

    return answers


def get_output_details() -> tuple:
    """
    Obtiene los detalles de salida del reporte desde el usuario.

    Returns:
    tuple: Ruta de salida y formato del nombre del archivo.
    """
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
            "message": "Ingrese el formato del nombre del archivo (e.g., {client_name}, {title}, {stime}, {ltime}, {author}, {subject}, {uuid}):",
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
    """
    Obtiene los detalles del cliente desde el usuario.

    Returns:
    tuple: Nombre del cliente y ruta del logo.
    """
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

    return client_name, client_logo


def select_tables(tables: pd.DataFrame) -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples tablas para incluir en el reporte.

    Args:
    tables (pd.DataFrame): DataFrame con las tablas disponibles.

    Returns:
    pd.DataFrame: DataFrame con las tablas seleccionadas.
    """
    # Crear una lista de opciones a partir del DataFrame
    choices = [{"name": row['Name'], "value": row['Callback']}
               for index, row in tables.iterrows()]

    # Preguntar al usuario para seleccionar múltiples tablas
    answers = questionary.checkbox(
        "Seleccionar las tablas que se incluirán en el reporte: ",
        choices=choices,
        instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)",
    ).ask()

    if not answers:
        print("No se seleccionaron tablas.")
        return pd.DataFrame()

    # Filtrar el DataFrame para obtener las tablas seleccionadas
    selected_tables = tables[tables['Callback'].isin(
        answers)].reset_index(drop=True)

    return selected_tables


def select_charts(charts: pd.DataFrame) -> pd.DataFrame:
    """
    Permite al usuario seleccionar múltiples gráficos para incluir en el reporte.

    Args:
    charts (pd.DataFrame): DataFrame con los gráficos disponibles.

    Returns:
    pd.DataFrame: DataFrame con los gráficos seleccionados.
    """
    # Crear una lista de opciones a partir del DataFrame
    choices = [{"name": row['Name'], "value": row['Callback']}
               for index, row in charts.iterrows()]

    # Preguntar al usuario para seleccionar múltiples gráficos
    answers = questionary.checkbox(
        "Seleccionar los gráficos que se incluirán en el reporte: ",
        choices=choices,
        instruction="(Utilice las flechas para desplazarse, <espacio> para seleccionar, <a> para alternar, <i> para invertir)",
    ).ask()

    if not answers:
        print("No se seleccionaron gráficos.")
        return pd.DataFrame()

    # Filtrar el DataFrame para obtener los gráficos seleccionados
    selected_charts = charts[charts['Callback'].isin(
        answers)].reset_index(drop=True)

    return selected_charts


class ListReorder:
    def __init__(self, items):
        self.items = items
        self.selected_idx = 0
        self.selecting = False
        self.done = False
        self.offset = 0
        self.height = 0

    def _print_instructions(self, stdscr):
        instructions = "Utilice ARRIBA/ABAJO para navegar. Pulse ESPACIO para seleccionar/deseleccionar, ENTER para aceptar, INICIO para ir al principio, FIN para ir al final, 'q' para salir."
        stdscr.addstr(0, 0, instructions)

    def _print_items(self, stdscr):
        for i in range(self.height):
            idx = i + self.offset
            if idx >= len(self.items):
                break
            display_text = f"({idx + 1}) {self.items.iloc[idx]['Name']}"
            if idx == self.selected_idx:
                if self.selecting:
                    stdscr.addstr(
                        i + 2, 0, f"↕️ ● {display_text}", curses.A_REVERSE)
                else:
                    stdscr.addstr(
                        i + 2, 0, f"» ● {display_text}")
            else:
                stdscr.addstr(i + 2, 0, f"  ○ {display_text}")

    def _handle_key_press(self, stdscr):
        key = stdscr.getch()
        if not self.selecting:
            if key == curses.KEY_UP and self.selected_idx > 0:
                self.selected_idx -= 1
                if self.selected_idx < self.offset:
                    self.offset -= 1
            elif key == curses.KEY_DOWN and self.selected_idx < len(self.items) - 1:
                self.selected_idx += 1
                if self.selected_idx >= self.offset + self.height:
                    self.offset += 1
            elif key == curses.KEY_HOME:
                self.selected_idx = 0
                self.offset = 0
            elif key == curses.KEY_END:
                self.selected_idx = len(self.items) - 1
                self.offset = max(0, len(self.items) - self.height)
            elif key == ord(' '):
                self.selecting = True
            elif key == curses.KEY_ENTER or key in [10, 13]:
                self.done = True
            elif key == ord('q'):
                self.done = True
        else:
            if key == curses.KEY_UP and self.selected_idx > 0:
                self.items.iloc[self.selected_idx], self.items.iloc[self.selected_idx -
                                                                    1] = self.items.iloc[self.selected_idx - 1].copy(), self.items.iloc[self.selected_idx].copy()
                self.selected_idx -= 1
                if self.selected_idx < self.offset:
                    self.offset -= 1
            elif key == curses.KEY_DOWN and self.selected_idx < len(self.items) - 1:
                self.items.iloc[self.selected_idx], self.items.iloc[self.selected_idx +
                                                                    1] = self.items.iloc[self.selected_idx + 1].copy(), self.items.iloc[self.selected_idx].copy()
                self.selected_idx += 1
                if self.selected_idx >= self.offset + self.height:
                    self.offset += 1
            elif key == ord(' '):
                self.selecting = False

    def _main(self, stdscr):
        curses.curs_set(0)  # Ocultar el cursor
        self.height = curses.LINES - 3  # Altura disponible para la lista

        while not self.done:
            stdscr.clear()
            self._print_instructions(stdscr)
            self._print_items(stdscr)
            self._handle_key_press(stdscr)
            stdscr.refresh()

    def reorder(self):
        curses.wrapper(self._main)
        return self.items


class DateSelector:
    def __init__(self,
                 message="Select a date",
                 starting_date=None,
                 min_date=None,
                 max_date=None,
                 week_start=-1,  # Start week on Sunday by default
                 navigate_keys=None,
                 change_year_key='y',
                 confirm_key='\n',
                 instructions=None,
                 enter_year_prompt="Enter year: ",
                 selected_date_message="Selected date: {date}"):

        self._message = message
        self._starting_date = starting_date or datetime.date.today()
        self._min_date = min_date or datetime.date(1900, 1, 1)
        self._max_date = max_date or datetime.date(2100, 12, 31)
        self._week_start = week_start
        self._selected_date = self._starting_date

        # Key bindings
        self._navigate_keys = navigate_keys or {
            'up': curses.KEY_UP,
            'down': curses.KEY_DOWN,
            'left': curses.KEY_LEFT,
            'right': curses.KEY_RIGHT
        }
        self._change_year_key = ord(change_year_key)
        self._confirm_key = ord(confirm_key)
        text_key = 'ENTER' if confirm_key == '\n' else confirm_key

        # Instructions
        self._instructions = instructions or {
            'navigation': "Welcome to «LogRhythm Report Tool». Before creating your report, we need to configure a few things.\nUse arrow keys to navigate, enter to select the date.",
            'change_year': f"Press '{change_year_key}' to change the year and '{text_key}' to confirm."
        }

        # Customizable messages
        self._enter_year_prompt = enter_year_prompt
        self._selected_date_message = selected_date_message

    def _render_calendar(self, stdscr):
        stdscr.clear()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Selected date
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Weekend days
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Weekdays

        # Render navigation instructions
        navigation_lines = self._instructions['navigation'].split('\n')
        for i, line in enumerate(navigation_lines):
            stdscr.addstr(i, 0, line, curses.color_pair(3))

        # Render selected date header
        stdscr.addstr(len(navigation_lines) + 1, 0, self._selected_date.strftime("%B %Y"), curses.color_pair(3))

        # Print the day headers
        days_header = [" Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        stdscr.addstr(len(navigation_lines) + 2, 0, " ".join(days_header), curses.color_pair(3))

        # Calculate start day and days in month
        first_day = self._selected_date.replace(day=1)
        start_day = (first_day.weekday() - self._week_start + 7) % 7
        days_in_month = (first_day + datetime.timedelta(days=32)).replace(day=1) - first_day

        # Render calendar days
        current_line = len(navigation_lines) + 3
        current_column = start_day * 3  # Adjusted spacing for alignment

        for day in range(1, days_in_month.days + 1):
            current_date = first_day.replace(day=day)
            color = curses.color_pair(3)  # Weekdays
            if current_date.weekday() >= 5:  # Saturday or Sunday
                color = curses.color_pair(2)  # Weekend days
            if current_date == self._selected_date:
                stdscr.addstr(current_line, current_column, f"[{day:2}]", curses.color_pair(1))
            else:
                stdscr.addstr(current_line, current_column, f" {day:2} ", color)
            current_column += 3  # Adjusted spacing for alignment
            if (start_day + day) % 7 == 0:
                current_line += 1
                current_column = 0

        # Render the message "Seleccione una fecha"
        stdscr.addstr(current_line + 2, 0, self._message, curses.color_pair(3))

        # Render change year instructions
        change_year_lines = self._instructions['change_year'].split('\n')
        for i, line in enumerate(change_year_lines):
            stdscr.addstr(current_line + 3 + i, 0, line, curses.color_pair(3))

        # Refresh screen
        stdscr.refresh()

    def _change_year(self, stdscr):
        curses.echo()
        stdscr.addstr(13, 0, self._enter_year_prompt, curses.color_pair(3))
        try:
            new_year = int(stdscr.getstr().decode())
            self._selected_date = self._selected_date.replace(year=new_year)
        except ValueError:
            pass
        curses.noecho()

    def _date_select(self, stdscr):
        while True:
            self._render_calendar(stdscr)
            key = stdscr.getch()
            if key == self._navigate_keys['up']:
                self._selected_date -= datetime.timedelta(weeks=1)
            elif key == self._navigate_keys['down']:
                self._selected_date += datetime.timedelta(weeks=1)
            elif key == self._navigate_keys['right']:
                self._selected_date += datetime.timedelta(days=1)
                if self._selected_date.month != (self._selected_date + datetime.timedelta(days=1)).month:
                    self._selected_date = self._selected_date.replace(day=1) + datetime.timedelta(days=31)
            elif key == self._navigate_keys['left']:
                self._selected_date -= datetime.timedelta(days=1)
                if self._selected_date.month != (self._selected_date - datetime.timedelta(days=1)).month:
                    self._selected_date = self._selected_date.replace(day=1) - datetime.timedelta(days=1)
            elif key == self._change_year_key:  # Change year
                self._change_year(stdscr)
            elif key == self._confirm_key:  # ENTER
                break

            if self._selected_date < self._min_date:
                self._selected_date = self._min_date
            elif self._selected_date > self._max_date:
                self._selected_date = self._max_date

    def select_date(self):
        def selector(stdscr):
            self._date_select(stdscr)
            stdscr.addstr(len(self._instructions['navigation'].split('\n')) + 12, 0, self._selected_date_message.format(date=self._selected_date), curses.color_pair(3))
            stdscr.refresh()
            stdscr.getch()

        curses.wrapper(selector)
        return self._selected_date


def select_date_range():
    from datetime import time, datetime

    selector = DateSelector(message = "Seleccione una fecha", 
                            enter_year_prompt = "Introduzca el año: ", 
                            selected_date_message = "Fecha seleccionada: {date}",
                            instructions =  {
                                'navigation': "Bienvenido a «LogRhythm Report Tool», para crear su reporte primero tenemos que configurar algunas cosas.\nUtilice las flechas del teclado «↑↓←→» para navegar, «ENTER» para seleccionar la fecha",
                                'change_year': f"Pulse «y» para cambiar el año y «ENTER» para confirmar."
                            })

    start_date = selector.select_date()
    end_date = selector.select_date()

    # Convertir las fechas seleccionadas a datetime
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    return (start_datetime, end_datetime)

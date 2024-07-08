import datetime
import curses
from typing import Dict, Optional, Union

class DateSelector:
    def __init__(self,
                 message: str = "Seleccione una fecha",
                 starting_date: Optional[datetime.date] = None,
                 min_date: Optional[datetime.date] = None,
                 max_date: Optional[datetime.date] = None,
                 week_start_sunday: bool = True,  # True means week starts on Sunday
                 navigate_keys: Optional[Dict[str, Union[int, str]]] = None,
                 change_year_key: str = 'y',
                 confirm_key: str = '\n',
                 cancel_key: str = 'c',
                 instructions: Optional[Dict[str, str]] = None,
                 enter_year_prompt: str = "Ingrese el año: ",
                 selected_date_message: str = "Fecha seleccionada: {date}",
                 cancel_message: str = "Selección de fecha cancelada."):

        self.message = message
        self.starting_date = starting_date or datetime.date.today()
        self.min_date = min_date or datetime.date(1900, 1, 1)
        self.max_date = max_date or datetime.date(2100, 12, 31)
        self.week_start_sunday = week_start_sunday
        self.selected_date = self.starting_date

        # Key bindings
        self.navigate_keys = navigate_keys or {
            'up': curses.KEY_UP,
            'down': curses.KEY_DOWN,
            'left': curses.KEY_LEFT,
            'right': curses.KEY_RIGHT
        }
        self.change_year_key = ord(change_year_key)
        self.confirm_key = ord(confirm_key)
        self.cancel_key = ord(cancel_key)
        text_key = 'ENTER' if confirm_key == '\n' else confirm_key

        # Instructions
        self.instructions = instructions or {
            'navigation': "Utilice las flechas del teclado «↑↓←→» para navegar, «ENTER» para seleccionar la fecha.",
            'change_year': f"Pulse «{change_year_key}» para cambiar el año, «{text_key}» para confirmar y «{cancel_key}» para cancelar."
        }

        # Customizable messages
        self.enter_year_prompt = enter_year_prompt
        self.selected_date_message = selected_date_message
        self.cancel_message = cancel_message

    def render_header(self, stdscr: 'curses.window') -> int:
        stdscr.clear()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Selected date
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Weekend days
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Weekdays

        # Get window dimensions
        max_y, max_x = stdscr.getmaxyx()

        # Render navigation instructions
        navigation_lines = self.instructions['navigation'].split('\n')
        for i, line in enumerate(navigation_lines):
            if i < max_y:
                stdscr.addstr(i, 0, line, curses.color_pair(3))
        return len(navigation_lines)

    def render_date_header(self, stdscr: 'curses.window', header_y: int) -> int:
        max_y, _ = stdscr.getmaxyx()
        if header_y < max_y:
            stdscr.addstr(header_y, 0, self.selected_date.strftime("%B %Y"), curses.color_pair(3))
        return header_y + 1

    def render_day_headers(self, stdscr: 'curses.window', days_header_y: int) -> int:
        max_y, _ = stdscr.getmaxyx()
        if days_header_y < max_y:
            days_header = [" Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"] if self.week_start_sunday else ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", " Do"]
            stdscr.addstr(days_header_y, 0, "  ".join(days_header), curses.color_pair(3))  # Adjust spacing for alignment
        return days_header_y + 1

    def render_calendar(self, stdscr: 'curses.window'):
        header_end_y = self.render_header(stdscr)
        date_header_y = self.render_date_header(stdscr, header_end_y)
        days_header_y = self.render_day_headers(stdscr, date_header_y)

        # Calculate start day and days in month
        first_day = self.selected_date.replace(day=1)
        if self.week_start_sunday:
            start_day = first_day.weekday() + 1 if first_day.weekday() != 6 else 0  # Adjust for Sunday start
        else:
            start_day = (first_day.weekday() + 1) % 7  # Adjust for Monday start

        days_in_month = (first_day + datetime.timedelta(days=32)).replace(day=1) - first_day

        current_line = days_header_y + 1
        current_column = start_day * 4  # Use 4 spaces for better alignment

        max_y, max_x = stdscr.getmaxyx()
        for day in range(1, days_in_month.days + 1):
            if current_line < max_y:
                current_date = first_day.replace(day=day)
                color = curses.color_pair(3)
                if current_date.weekday() >= 5:  # Saturday or Sunday
                    color = curses.color_pair(2)
                if current_date == self.selected_date:
                    stdscr.addstr(current_line, current_column, f"[{day:2}]", curses.color_pair(1))
                else:
                    stdscr.addstr(current_line, current_column, f" {day:2} ", color)
                current_column += 4  # Increment by 4 to ensure proper spacing
                if current_column >= max_x or (start_day + day) % 7 == 0:
                    current_line += 1
                    current_column = 0

        message_y = current_line + 2
        if message_y < max_y:
            stdscr.addstr(message_y, 0, self.message, curses.color_pair(3))

        change_year_lines = self.instructions['change_year'].split('\n')
        for i, line in enumerate(change_year_lines):
            instruction_y = current_line + 3 + i
            if instruction_y < max_y:
                stdscr.addstr(instruction_y, 0, line, curses.color_pair(3))

        stdscr.refresh()

    def change_year(self, stdscr: 'curses.window'):
        curses.echo()
        stdscr.addstr(0, 0, self.enter_year_prompt, curses.color_pair(3))
        try:
            new_year = int(stdscr.getstr().decode())
            self.selected_date = self.selected_date.replace(year=new_year)
        except ValueError:
            pass
        curses.noecho()

    def date_select(self, stdscr: 'curses.window'):
        while True:
            self.render_calendar(stdscr)
            key = stdscr.getch()
            if key == self.navigate_keys['up']:
                self.selected_date -= datetime.timedelta(weeks=1)
            elif key == self.navigate_keys['down']:
                self.selected_date += datetime.timedelta(weeks=1)
            elif key == self.navigate_keys['right']:
                self.selected_date += datetime.timedelta(days=1)
            elif key == self.navigate_keys['left']:
                self.selected_date -= datetime.timedelta(days=1)
            elif key == self.change_year_key:
                self.change_year(stdscr)
            elif key == self.confirm_key:
                break
            elif key == self.cancel_key:
                self.selected_date = None
                break

            if self.selected_date:
                if self.selected_date < self.min_date:
                    self.selected_date = self.min_date
                elif self.selected_date > self.max_date:
                    self.selected_date = self.max_date

    def select_date(self) -> Optional[datetime.date]:
        def selector(stdscr: 'curses.window'):
            self.date_select(stdscr)
            if self.selected_date:
                stdscr.addstr(curses.LINES - 1, 0, self.selected_date_message.format(date=self.selected_date), curses.color_pair(3))
            else:
                stdscr.addstr(curses.LINES - 1, 0, self.cancel_message, curses.color_pair(2))
            stdscr.refresh()
            stdscr.getch()

        curses.wrapper(selector)
        return self.selected_date

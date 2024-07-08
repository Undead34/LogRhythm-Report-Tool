import datetime
import curses

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

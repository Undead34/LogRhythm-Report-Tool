import curses

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


from reportlab.platypus import Table as RLTable, Paragraph, Indenter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib import colors
import pandas as pd
from typing import List, Optional, Dict
from src.themes.theme import CustomTableStyle, CustomTableStyles, Theme

class Cell:
    def __init__(self, content: str, style: Optional[Dict] = None):
        self.content = content
        self.style = style or {}

class Row:
    def __init__(self, cells: List[Cell]):
        self.cells = cells

class Table:
    def __init__(self, df: pd.DataFrame, 
                 style: CustomTableStyle,
                 column_names: Optional[List[str]] = None, 
                 mode: str = 'auto', 
                 padding: int = 12, 
                 indent: int = 0,
                 include_totals: bool = False, 
                 totals_columns: Optional[List[int]] = None,
                 max_width: Optional[int] = None, 
                 min_width: Optional[int] = None, 
                 truncate_text: bool = False, 
                 truncate_length: int = 20):
        self.df = df
        self.column_names = column_names or df.columns.tolist()
        self.mode = mode
        self.padding = padding
        self.indent = indent
        self.include_totals = include_totals
        self.totals_columns = totals_columns
        self.max_width = max_width
        self.min_width = min_width
        self.truncate_text = truncate_text
        self.truncate_length = truncate_length
        self.style = style or Theme().get_style(CustomTableStyles.DEFAULT)

        self.validate()
        self.rows = self._create_rows()

    def validate(self):
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("df should be a pandas DataFrame")
        if len(self.column_names) != self.df.shape[1]:
            raise ValueError("column_names length should match the number of DataFrame columns")

    def to_data(self) -> List[List[str]]:
        return [[cell.content for cell in row.cells] for row in self.rows]

    def render(self):
        data = self.to_data()
        if not data or len(data) == 1:
            return []

        rows, cols = len(data), len(data[0])
        usable_width = LETTER[0] - 5 * cm  # assuming left and right margin combined to be 5 cm

        def calculate_column_widths(data, styles, padding):
            return [
                max(stringWidth(str(cell), styles[i % len(styles)]['fontName'], styles[i % len(styles)]['fontSize']) + padding for i, cell in enumerate(column))
                for column in zip(*data)
            ]

        header_styles = [self.style.get_cell_styles(row=0)]
        content_styles = [self.style.get_cell_styles(row=1)]

        header_widths = calculate_column_widths(data[:1], header_styles, self.padding)
        content_widths = calculate_column_widths(data[1:], content_styles, self.padding)
        col_widths = [max(h, c) for h, c in zip(header_widths, content_widths)]

        total_width = sum(col_widths)

        if self.max_width:
            col_widths = [min(w, self.max_width) for w in col_widths]
        if self.min_width:
            col_widths = [max(w, self.min_width) for w in col_widths]

        if self.mode == 'equal':
            col_widths = [usable_width / cols] * cols
        elif self.mode == 'fit-full':
            col_widths = self._adjust_widths_fit_full(col_widths, total_width, usable_width)
        elif self.mode == 'auto':
            col_widths = self._adjust_widths_auto_v2(col_widths, total_width, usable_width, header_widths)
        else:  # Default to 'fit'
            if total_width > usable_width:
                scale_factor = usable_width / total_width
                col_widths = [w * scale_factor for w in col_widths]

        if self.include_totals and self.totals_columns:
            totals_row = []
            for col in range(cols):
                if col in self.totals_columns:
                    try:
                        total = sum(float(data[row][col]) for row in range(1, rows))
                        totals_row.append(total)
                    except ValueError:
                        totals_row.append('N/A')
                else:
                    totals_row.append('')
            data.append(totals_row)

        table_data = [
            [
                Paragraph(str(cell.content)[:self.truncate_length] + '...' if self.truncate_text and len(str(cell.content)) > self.truncate_length else str(cell.content),
                          self.style.get_paragraph_style(row_index, col_index))
                for col_index, cell in enumerate(row.cells)
            ] 
            for row_index, row in enumerate(self.rows)
        ]

        table = RLTable(table_data, colWidths=col_widths)
        table.setStyle(self.style.table_style)

        return [Indenter(left=self.indent), table]

    def _create_rows(self) -> List[Row]:
        header_cells = [Cell(name) for name in self.column_names]
        header_row = Row(header_cells)

        data_rows = []
        for _, row in self.df.iterrows():
            cells = [Cell(str(cell)) for cell in row]
            data_rows.append(Row(cells))

        return [header_row] + data_rows

    def _adjust_widths_fit_full(self, col_widths, total_width, usable_width):
        if total_width < usable_width:
            additional_width = usable_width - total_width
            col_widths = [w + (w / total_width) * additional_width for w in col_widths]
        else:
            scale_factor = usable_width / total_width
            col_widths = [w * scale_factor for w in col_widths]
        return col_widths

    def _adjust_widths_auto_v2(self, col_widths, total_width, usable_width, min_header_widths):
        if total_width > usable_width:
            scale_factor = usable_width / total_width
            col_widths = [w * scale_factor for w in col_widths]

        total_width = sum(col_widths)
        if total_width < usable_width:
            additional_width = usable_width - total_width
            col_widths = [w + additional_width / len(col_widths) for w in col_widths]
        
        for i in range(len(col_widths)):
            if col_widths[i] < min_header_widths[i]:
                col_widths[i] = min_header_widths[i]

        total_width = sum(col_widths)
        if total_width > usable_width:
            remaining_width = usable_width - sum(min_header_widths)
            remaining_col_widths = [w - min_header_widths[i] for i, w in enumerate(col_widths)]
            remaining_total_width = sum(remaining_col_widths)
            if remaining_total_width > 0:
                scale_factor = remaining_width / remaining_total_width
                for i in range(len(col_widths)):
                    col_widths[i] = min_header_widths[i] + (col_widths[i] - min_header_widths[i]) * scale_factor
            else:
                col_widths = min_header_widths

        return col_widths

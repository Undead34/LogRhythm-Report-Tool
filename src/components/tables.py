from reportlab.platypus import Table as RLTable, Paragraph, Indenter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.lib import colors
import pandas as pd
from typing import List, Optional, Dict
from src.themes.theme import Theme, CustomTableStyles

class Cell:
    def __init__(self, content: str, style: Optional[Dict] = None):
        self.content = content
        self.style = style or {}

class Row:
    def __init__(self, cells: List[Cell]):
        self.cells = cells

class Table:
    def __init__(self, df: pd.DataFrame, column_names: Optional[List[str]] = None, cell_styles: Optional[List[Dict]] = None, table_style_name: Optional[str] = None):
        self.df = df
        self.column_names = column_names or df.columns.tolist()
        self.cell_styles = cell_styles or [{}] * df.shape[1]
        self.table_style_name = table_style_name or CustomTableStyles.DEFAULT.value
        self.validate()
        self.rows = self._create_rows()

    def validate(self):
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("df should be a pandas DataFrame")
        if len(self.column_names) != self.df.shape[1]:
            raise ValueError("column_names length should match the number of DataFrame columns")
        if len(self.cell_styles) != self.df.shape[1]:
            raise ValueError("cell_styles length should match the number of DataFrame columns")

    def _create_rows(self) -> List[Row]:
        header_cells = [Cell(name, style=self.cell_styles[i]) for i, name in enumerate(self.column_names)]
        header_row = Row(header_cells)

        data_rows = []
        for _, row in self.df.iterrows():
            cells = [Cell(str(cell), style=self.cell_styles[i]) for i, cell in enumerate(row)]
            data_rows.append(Row(cells))

        return [header_row] + data_rows

    def to_data(self) -> List[List[str]]:
        return [[cell.content for cell in row.cells] for row in self.rows]

    def create_pdf_table(self, theme: Theme, mode='auto', padding=12, sangria=0,
                         include_totals=False, totals_columns=None,
                         max_width=None, min_width=None, truncate_text=False, truncate_length=20):
        data = self.to_data()
        if not data or len(data) == 1:
            return []

        rows, cols = len(data), len(data[0])
        usable_width = LETTER[0] - 2 * cm - sangria  # 2 cm margin on each side

        def calculate_column_widths(data, style, padding):
            return [
                max(stringWidth(str(cell), style['fontName'], style['fontSize']) + padding for cell in column)
                for column in zip(*data)
            ]

        header_widths = calculate_column_widths(data[:1], {'fontName': 'Helvetica-Bold', 'fontSize': 12}, padding)
        content_widths = calculate_column_widths(data[1:], {'fontName': 'Helvetica', 'fontSize': 10}, padding)
        col_widths = [max(h, c) for h, c in zip(header_widths, content_widths)]

        total_width = sum(col_widths)

        if max_width:
            col_widths = [min(w, max_width) for w in col_widths]
        if min_width:
            col_widths = [max(w, min_width) for w in col_widths]

        if mode == 'equal':
            col_widths = [usable_width / cols] * cols
        elif mode == 'fit-full':
            col_widths = self._adjust_widths_fit_full(col_widths, total_width, usable_width)
        elif mode == 'auto':
            col_widths = self._adjust_widths_auto_v2(col_widths, total_width, usable_width, header_widths)
        else:  # Default to 'fit'
            if total_width > usable_width:
                scale_factor = usable_width / total_width
                col_widths = [w * scale_factor for w in col_widths]

        if include_totals and totals_columns:
            totals_row = []
            for col in range(cols):
                if col in totals_columns:
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
                Paragraph(str(cell.content)[:truncate_length] + '...' if truncate_text and len(str(cell.content)) > truncate_length else str(cell.content),
                          self._get_paragraph_style(cell.style))
                for cell in row.cells
            ] 
            for i, row in enumerate(self.rows)
        ]

        table = RLTable(table_data, colWidths=col_widths)
        custom_style = theme.get_style(self.table_style_name)
        table.setStyle(custom_style)

        return [Indenter(left=sangria), table]

    def _get_paragraph_style(self, style: Dict):
        # Crear un estilo de párrafo a partir del diccionario de estilo
        from reportlab.lib.styles import ParagraphStyle
        return ParagraphStyle(
            name='CustomStyle',
            fontName=style.get('fontName', 'Helvetica'),
            fontSize=style.get('fontSize', 10),
            textColor=style.get('textColor', colors.black),
        )

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

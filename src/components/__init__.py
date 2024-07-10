from reportlab.platypus import Paragraph, ListFlowable, ListItem, PageBreak, Spacer
from reportlab.lib.units import cm

from .charts import Bar, Pie, HeatMap, Historigram, Line, Box, Stacked, Scatter, Pareto, Bubble
from .cover import Cover
from .tables import Cell, Table, Row


class ListElement():
    def __init__(self, items: list[Paragraph], *args, **kwargs) -> None:
        self.items = items
        self.elements = ListFlowable([ListItem(item, leftIndent = 1 * cm) for item in self.items], *args, **kwargs)
    
    def render(self):
        return self.elements
from reportlab.platypus import Paragraph, ListFlowable, ListItem
from reportlab.lib.units import cm

from .charts import *
from .cover import *
from .tables import *

class ListElement():
    def __init__(self, items: list[Paragraph], *args, **kwargs) -> None:
        self.items = items
        self.elements = ListFlowable([ListItem(item, leftIndent = 1 * cm) for item in self.items], *args, **kwargs)
    
    def render(self):
        return self.elements
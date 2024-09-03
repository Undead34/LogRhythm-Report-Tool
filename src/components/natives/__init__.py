from reportlab.platypus import Paragraph as NativeParagraph, Image as NativeImage

from src.utils import Element

class Paragraph(NativeParagraph, Element):
    def __init__(self, text: str, className: str = "Paragraph", *args, **kwargs) -> None:
        NativeParagraph.__init__(self, text, *args, **kwargs)
        Element.__init__(self)
        self.className = className

    def render(self):
        return self

class Image(NativeImage, Element):
    def __init__(self, *args, **kwargs) -> None:
        NativeImage.__init__(self, *args, **kwargs)
        Element.__init__(self)
        self.className = "Image"
    
    def render(self):
        return self

# from reportlab.lib.units import cm
# from .charts import *
# from .cover import *
# from .tables import *
# class ListElement():
#     def __init__(self, items: list[Paragraph], *args, **kwargs) -> None:
#         self.items = items
#         self.elements = ListFlowable([ListItem(item, leftIndent = 1 * cm) for item in self.items], *args, **kwargs)
#     def render(self):
#         return self.elements
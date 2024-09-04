from reportlab.platypus import Paragraph as NativeParagraph, Image as NativeImage

from src.utils import Element

class Paragraph(Element):
    def __init__(self, text: str, className: list[str] | str, *args, **kwargs) -> None:
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.text = text

        if isinstance(className, list):
            if "paragraph" not in className:
                className.append("paragraph")
            self.className = className
        else:
            self.className = [className, "paragraph"]

    def render(self, styles):
        return NativeParagraph(self.text, style=styles, *self.args, **self.kwargs)

class Image(NativeImage, Element):
    def __init__(self, *args, **kwargs) -> None:
        NativeImage.__init__(self, *args, **kwargs)
        Element.__init__(self)
        self.className = ["image"]
    
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
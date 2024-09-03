from src.templates.generic import GenericTemplate

from .sections import CoverPage
from .canvas import Canvas
from .theme import Theme

class GeneralTemplate(GenericTemplate):
    def __init__(self, output_path: str, metadata: dict) -> None:
        super().__init__(output_path, metadata, theme=Theme, canvas=Canvas)

        self.elements += CoverPage().render()

        self.theme.apply(self.elements)
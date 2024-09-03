from src.templates.generic import GenericTemplate

from .sections import cover_page
from .canvas import Canvas
from .theme import Theme

class GeneralTemplate(GenericTemplate):
    def __init__(self, output_path: str, metadata: dict) -> None:
        super().__init__(output_path, metadata, theme=Theme, canvas=Canvas)

        self.theme

        self.elements += cover_page()
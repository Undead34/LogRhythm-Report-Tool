from types import MappingProxyType
from .general import GeneralTemplate

class Templates:
    def __init__(self, output_path: str, metadata: dict) -> None:
        templates = {
            "general": GeneralTemplate(output_path, metadata)
        }
        self._templates = MappingProxyType(templates)

    @property
    def templates(self):
        return self._templates
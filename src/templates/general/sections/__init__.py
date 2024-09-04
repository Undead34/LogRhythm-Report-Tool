from reportlab.lib.units import cm

from src.utils import ElementList, Element
from src.components import Paragraph, Spacer, Image, PageBreak

class CoverPage(Element):
    def __init__(self) -> None:
        super().__init__()
        self.className = ["CoverPage"]

    def render(self) -> ElementList:
        elements = ElementList()

        elements += Spacer(0, 4.95 * cm) # 4.95 cm is the height of the image
        elements += Spacer(0, 3.5 * cm)  # 3.5 cm is the padding between the image and the title

        elements += Paragraph("Banco Venezolano de Crédito", className="TitleCoverText")
        elements += [Paragraph(" ", className="TitleCoverText") for _ in range(2)]
        elements += Paragraph("Pruebas de Penetración Externa", className="TitleCoverText")
        elements += [Paragraph(" ", className="TitleCoverText") for _ in range(2)]
        elements += Paragraph("Informe Técnico", className="TitleCoverText")

        elements += Spacer(0, 3.5 * cm)  # 3.5 cm is the padding between the image and the title

        elements += Image(filename="./assets/images/netready-h.png", width=8.55 * cm, height=3.86 * cm)

        elements += PageBreak()

        return elements
    
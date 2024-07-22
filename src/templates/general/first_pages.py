from reportlab.platypus import Paragraph, PageBreak
from datetime import datetime

from src.themes.theme import Theme, ParagraphStyles, FontsNames
from src.components import  ListElement, Cover
from src.utils import ElementList

from reportlab.lib.units import cm

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.app import Config

def cover(config: 'Config', metadata: dict, theme: Theme):
    def format_date(date: datetime) -> str:
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

    today = format_date(datetime.now())
    start, end = map(format_date, config.date_range)
    client_name, client_logo = config.client_details

    text = f"""
        **Reporte preparado para:** {client_name}<br/>
        **Fecha de creación:** {today}<br/>
        **Periodo del reporte:** Entre {start} y {end}<br/>
        **Preparado por:** {metadata.get("author", "Netready Solutions")}
    """

    text = theme.replace_bold_with_font(text)
    footer = f"© {datetime.now().year} Soluciones Netready, C.A. Todos los Derechos Reservados."

    return Cover(metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, theme).render()


def introduction(theme: Theme):
    style = theme.get_style

    elements = ElementList()
    elements += Paragraph("Introducción".upper(), style(ParagraphStyles.TITLE_1))
    elements += Paragraph("1. Objetivo del Reporte", style(ParagraphStyles.TITLE_2))

    intro_text =[
        """
        **Propósito**: Proporcionar una visión detallada y automatizada del estado del Sistema de Gestión de Información y Eventos de Seguridad (SIEM), 
        destacando los aspectos clave relacionados con la seguridad, el rendimiento y la conformidad.
        """,
        """
        **Alcance**: Este reporte cubre la actividad del SIEM durante el periodo especificado,
            incluyendo la identificación de atacantes, vulnerabilidades, alarmas, 
            fallas operativas, detalles de logs, estadísticas de componentes y resúmenes automáticos.
        """,
        """
        **Metodología**: Los datos presentados han sido recopilados y analizados utilizando herramientas automatizadas que integran y correlacionan información de múltiples fuentes. 
        Los gráficos y tablas incluidos son el resultado de análisis estadísticos diseñados para resaltar tendencias significativas y puntos críticos.
        """,
        """**Estructura del Reporte**: El reporte se divide en varias secciones clave:"""]

    elements += [Paragraph(theme.replace_bold_with_font(text), style(ParagraphStyles.SUB_TEXT_NORMAL)) for text in intro_text]

    sections = [
        "**Indicadores de cumplimiento de SLA y Tiempos de Gestión**: Un análisis detallado de los indicadores de nivel de servicio (SLA) y tiempos de respuesta para la gestión de incidentes y eventos.",
        "**Análisis de Eventos**: Un desglose de los eventos capturados por el SIEM, categorizados por tipo, gravedad y fuente.",
        "**Detección de Amenazas**: Información sobre amenazas detectadas, incluyendo atacantes identificados, métodos de ataque y medidas de mitigación implementadas."
    ]

    sections = [Paragraph(theme.replace_bold_with_font(section), style(ParagraphStyles.SUB_LIST)) for section in sections]

    elements += ListElement(sections, bulletFontName=FontsNames.ARIALNARROW.value, bulletType='bullet', bulletColor=theme.colors.get("light_blue"), leftIndent=-0.5 * cm).render()
    elements += PageBreak()

    return elements

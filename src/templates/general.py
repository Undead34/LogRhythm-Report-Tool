from src.utils import ElementList
from .canvas import Canvas

from src.themes import theme
from src.components import Bar, Cover

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.databases import MSQLServer
    from src.app import Config
    from src.reports.skeleton import Report

from datetime import datetime

class GeneralTemplate():
    canvasmaker: Canvas
    elements: ElementList

    def __init__(self, report: 'Report', queries, database: 'MSQLServer', metadata: dict, config: 'Config') -> None:
        self.report, self.queries, self.db, self.metadata, self.config = report, queries, database, metadata, config

        Canvas.metadata = metadata

        self.canvasmaker = Canvas
        self.elements = ElementList()
        self.theme = self.report.theme
        self.style = self.theme.get_style
        self.paragraph_styles = theme.ParagraphStyles


    def top_alarms(self):
        df = self.db.get_alarms_information()
        df = df.groupby('AlarmRuleName').size().reset_index(name='Count')
        df = df.sort_values(by='Count', ascending=False)  # Ordena de mayor a menor

        bar = Bar(df, x_col='AlarmRuleName', y_col='Count', show_xticks=False, show_legend=True)

        return [bar.plot()]

    def run(self):
        today = datetime.now()
        (start, end) = self.config.date_range
        
        today = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end = end.strftime('%Y-%m-%dT%H:%M:%SZ')

        client_name = self.config.client_details[0]
        client_logo = self.config.client_details[1]

        text = f"""
            **Reporte preparado para:** {client_name}<br/>
            **Fecha de creación:** {today}<br/>
            **Periodo del reporte:** Entre {start} y {end}<br/>
            **Preparado por:** {self.metadata.get("author", "Netready Solutions")}
        """

        text = self.theme.replace_bold_with_font(text)

        footer = f"© {datetime.now().year} Soluciones Netready, C.A. All Rights Reserved."

        self.elements += Cover(self.metadata.get("title", ""), "./assets/images/netready.png", client_logo, text, footer, self.theme).render()

        self.elements += self.top_alarms()

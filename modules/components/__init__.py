from reportlab.platypus import PageBreak, Image, Spacer, Paragraph
from reportlab.lib.units import cm

from datetime import datetime
import pandas as pd

from modules.template.theme import ParagraphStyles
from utils import ElementList
from .charts import Charts
from .tables import Tables

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from modules.report import Report


class Components:
    def __init__(self, report: 'Report') -> None:
        self.report = report
        self.theme = report.theme
        self.db = report.database
        self.pkg = report.packages
        self.charts = Charts(self)
        self.tables = Tables(self)

        # Atributo privado _available_tables
        self._available_tables = pd.DataFrame([
            {
                "ID": "table_of_entities",
                "Name": "Tabla de Entidades en LogRhythm, contiene las columnas [«Entity ID», «Entity Name»].",
                "Description": "",
                "Callback": self.tables.table_of_entities
            },
            {
                "ID": "alarm_status_table",
                "Name": "Tabla de estados de alarma reportados en LogRhythm.",
                "Description": (
                    "Muestra cuantas alarmas están marcadas como:\n"
                    "   'Auto Closed', 'Reported', 'Resolved', 'False Positive' o 'Monitor'\n\n"
                    "Se excluyen los estados de alarma 'Nueva' y 'OpenAlarm', contiene las columnas:\n"
                    "   [«Entity Name», «Alarm Name», «Auto Closed»?, «Reported»?, «Resolved»?, «False Positive»?, «Monitor»?].\n"
                ),
                "Callback": self.tables.alarm_status_table
            },
            {
                "ID": "table_of_log_source_type",
                "Name": "table_of_log_source_type",
                "Description": "",
                "Callback": self.tables.table_of_log_source_type
            }
        ])

        # Atributo privado _available_charts
        self._available_charts = pd.DataFrame([
            {
                "ID": "trends_in_alarm_activation_graph",
                "Name": "Gráfico de Tendencias en la Activación de Alarmas",
                "Description": "Este gráfico muestra la evolución temporal y la frecuencia de activación de diferentes alarmas, permitiendo identificar tendencias y picos en los datos.",
                "Callback": self.charts.trends_in_alarm_activation_graph
            },
            {
                "ID": "stacked_bar_chart_by_alarm_status",
                "Name": "Gráfico de Distribución de Alarmas por Estado",
                "Description": "Este gráfico de barras apiladas muestra la distribución de diferentes tipos de alarmas según su estado. Las alarmas con estado 'New' y 'Open Alarm' han sido excluidas para una mejor claridad.",
                "Callback": self.charts.stacked_bar_chart_by_alarm_status
            },
            {
                "ID": "stacked_bar_chart_by_alarm_type",
                "Name": "Gráfico de Barras Apiladas por Tipo de Alarma y Fecha",
                "Description": "Este gráfico de barras apiladas muestra la cantidad de activaciones de diferentes alarmas a lo largo del tiempo. Se han seleccionado las diez alarmas con el mayor número total de activaciones durante todo el período analizado.",
                "Callback": self.charts.stacked_bar_chart_by_alarm_type
            },
            {
                "ID": "heatmap_alarms_by_day_and_hour",
                "Name": "Mapa de Calor de Activaciones de Alarmas",
                "Description": "Este mapa de calor muestra la frecuencia de activaciones de alarmas en diferentes días y horas, permitiendo identificar patrones temporales de activaciones.",
                "Callback": self.charts.heatmap_alarms_by_day_and_hour
            },
            {
                "ID": "scatter_plot_time_to_detection",
                "Name": "Gráfico de Dispersión de Duración de Alarmas",
                "Description": "Este gráfico de dispersión muestra la duración de cada activación de alarma, ayudando a identificar alarmas que tienen una duración inusualmente larga.",
                "Callback": self.charts.scatter_plot_time_to_detection
            },
            {
                "ID": "box_plot_time_to_detection",
                "Name": "box_plot_alarm_durations",
                "Callback": self.charts.box_plot_time_to_detection
            },
            {
                "ID": "heatmap_alarms_by_date_and_hour",
                "Name": "heatmap_alarms_by_date_and_hour",
                "Callback": self.charts.heatmap_alarms_by_date_and_hour
            }
        ])

    def get_tables(self) -> pd.DataFrame:
        return self._available_tables.copy()

    def get_charts(self):
        return self._available_charts.copy()

    def cover_page(self, signature: dict, name: str, logo: str):
        t = self.theme
        e = ElementList()

        e += Image("./assets/images/netready.png",
                   width=3.67 * cm,
                   height=3.12 * cm,
                   hAlign="CENTER")

        e += Spacer(0, 4.5 * cm)
        e += Paragraph(signature["title"],
                       t.get_style(ParagraphStyles.NR_TITULO_1))
        e += Spacer(0, 3.5 * cm)

        e += Image(logo,
                   width=10.37 * cm,
                   height=2.46 * cm,
                   hAlign="CENTER")

        e += Spacer(0, 3 * cm)

        today = datetime.now()
        e += Paragraph(f"""
        <font face=\"Arial-Narrow-Bold\">Reporte preparado para:</font> {name}<br/>
        <font face=\"Arial-Narrow-Bold\">Fecha de creación:</font> {today.strftime('%Y-%m-%dT%H:%M:%SZ')}<br/>
        <font face=\"Arial-Narrow-Bold\">Periodo del reporte:</font> Entre {self.db._start_date} y {self.db._end_date}<br/>
        <font face=\"Arial-Narrow-Bold\">Preparado por:</font> {signature['author']}
        """, self.theme.get_style(ParagraphStyles.NR_TEXTO_1))

        e += Paragraph(f"© {today.year} Soluciones Netready, C.A. All Rights Reserved.",
                    self.theme.get_style(ParagraphStyles.NR_TEXTO_ITALIC))

        e += PageBreak()

        return e

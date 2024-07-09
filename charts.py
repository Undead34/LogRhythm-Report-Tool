import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from uuid import uuid4 as v4
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import cm
from matplotlib.ticker import PercentFormatter
from utils import ElementList
from babel.numbers import format_number
from typing import TYPE_CHECKING, List, Union

from src.themes.theme import ParagraphStyles
from modules.components.draw import Draw

if TYPE_CHECKING:
    from modules.components import Components

class Charts:
    def __init__(self, components: 'Components') -> None:
        self._components = components
        self._theme = components.theme
        self._db = components.db
        self._pkg = components.pkg
        self._draw = Draw(self)

    def generate_report_elements(self, title: str, description: List[str], figures: Union[str, List[str]]) -> ElementList:
        elements = ElementList()

        if isinstance(figures, str):
            figures = [figures]

        for figure_src in figures:
            elements += Image(figure_src, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")

        elements += Paragraph(title, self._theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))

        for desc in description:
            elements += Paragraph(self.replace_bold_with_font(desc), self._theme.get_style(ParagraphStyles.NR_TEXTO_1))
        
        return elements

    def replace_bold_with_font(self, text: str) -> str:
        import re
        return re.sub(r'\*\*(.*?)\*\*', r'<font face="Arial-Narrow-Bold">\1</font>', text)

    def trends_in_alarm_activation_graph(self) -> ElementList:
        df = self._db.get_alarms_information()

        if df.empty:
            return [Paragraph("No hay datos disponibles para mostrar el histograma.", self._theme.get_style(ParagraphStyles.NR_TEXTO_NGRAFICO))]

        # Convertir y agrupar datos
        df['AlarmDate'] = pd.to_datetime(df['AlarmDate']).dt.floor('d')
        df = df.groupby(['AlarmDate', 'AlarmRuleName', 'AlarmPriority']).size().reset_index(name='Counts')

        priority = 55

        low_priority = df[df['AlarmPriority'] < priority]
        low_priority = low_priority.groupby('AlarmDate')['Counts'].sum().reset_index()
        low_priority['AlarmRuleName'] = 'Low Priority'

        df = df[df['AlarmPriority'] >= priority]
        df = pd.concat([df, low_priority], ignore_index=True)

        # Ordenar por 'Counts' para el split, pero mantener el orden por 'AlarmDate' dentro de cada grupo
        df_sorted_by_counts = df.sort_values(by='Counts', ascending=False).reset_index(drop=True)

        figures = []
        num_items = len(df_sorted_by_counts)
        num_chunks = num_items // 20 + (1 if num_items % 20 != 0 else 0)

        for i in range(num_chunks):
            start_idx = i * 20
            end_idx = start_idx + 20
            chunk_df = df_sorted_by_counts[start_idx:end_idx].sort_values(by='AlarmDate')
            figure = self._draw.histogram(chunk_df, x_col='AlarmDate', y_col='Counts', category_col='AlarmRuleName')
            figures.append(figure)

        description = [
            "Este gráfico **proporciona** una visualización detallada de la evolución temporal de diferentes alarmas...",
        ]

        elements = self.generate_report_elements("Alarm Activation Trends", description, figures)

        return elements

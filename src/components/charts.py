from reportlab.platypus import Image
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import pandas as pd
import os
from uuid import uuid4 as v4
import seaborn as sns

from typing import Optional
import random

class BaseChart():
    def __init__(self) -> None:
        pass

    def _save_chart(self) -> str:
        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output), 0o777, True)
        
        return output
    
    def plot(self):
        output = self._save_chart()
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        plt.close()

        return Image(output, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")

    def get_palette(self, n: int):
        base_colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611']
        
        if n <= len(base_colors):
            return base_colors[:n]
        else:
            additional_colors = sns.color_palette('husl', n - len(base_colors))
            return base_colors + additional_colors

class Bar(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, title: str | None = None, orientation: str = "vertical", show_xticks: bool = True, show_legend: bool = True, legend_title: str = "Categories", axies_labels=False) -> None:
        super().__init__()

        colors = self.get_palette(len(df))
        
        plt.figure(figsize=(12, 8))
        if orientation == "horizontal":
            bars = plt.barh(df[x_col], df[y_col], color=colors)
            if axies_labels:
                plt.xlabel(y_col)
                plt.ylabel(x_col)
        else:
            bars = plt.bar(df[x_col], df[y_col], color=colors)
            if axies_labels:
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            if not show_xticks:
                plt.xticks([])
        if title:
            plt.title(title)
        
        if show_legend:
            legend_labels = [f"{label} ({count})" for label, count in zip(df[x_col], df[y_col])]
            plt.legend(bars, legend_labels, title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

class Line(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None, category_col: Optional[str] = None, show_legend: bool = True, show_max_annotate: bool = True, axis_labels: bool = True) -> None:
        super().__init__()

        colors = self.get_palette(df[category_col].nunique() if category_col else 1)
        
        plt.figure(figsize=(18, 10))

        if category_col:
            for i, (name, group) in enumerate(df.groupby(category_col)):
                plt.plot(group[x_col], group[y_col], label=f"{name}", color=colors[i % len(colors)])
                
                # Agregar anotación y línea vertical si el grupo tiene solo un evento
                if group['Counts'].sum() == 1:
                    event_date = group[x_col].iloc[0]
                    plt.axvline(x=event_date, color=colors[i % len(colors)], linestyle='--')

                # Anotar el máximo valor
                if show_max_annotate:
                    max_count = group[y_col].max()
                    max_date = group[x_col][group[y_col].idxmax()]
                    plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, random.randint(0, 12)), ha='center', color=colors[i % len(colors)])
        else:
            plt.bar(df[x_col], df[y_col], color=colors[0])
            
            # Agregar anotación y línea vertical si el total de eventos es 1
            if df['Counts'].sum() == 1:
                event_date = df[x_col].iloc[0]
                plt.axvline(x=event_date, color=colors[0], linestyle='--')
            
            # Anotar el máximo valor
            if show_max_annotate:
                max_count = df[y_col].max()
                max_date = df[x_col][df[y_col].idxmax()]
                plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[0])

        # Añadir el número total de eventos
        total_events = df[y_col].sum()
        plt.annotate(f'Total Events: {total_events}', xy=(0.99, 0.01), xycoords='axes fraction', ha='right', va='bottom', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

        if title:
            plt.title(title)
        if axis_labels:
            plt.xlabel(x_col)
            plt.ylabel(y_col)
        
        if show_legend:
            plt.legend(title=category_col if category_col else 'Legend')
        
        plt.tight_layout()

class Pie():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class HeatMap():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Historigram():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Box():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Stacked():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Scatter():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Pareto():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Bubble():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

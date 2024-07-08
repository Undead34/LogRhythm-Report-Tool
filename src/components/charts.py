from reportlab.platypus import Image
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import pandas as pd
import os
from uuid import uuid4 as v4
import seaborn as sns


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

class Pie():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class HeatMap():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Historigram():
    def __init__(self, df: pd.DataFrame) -> None:
        BaseChart.__init__()

class Line():
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

from reportlab.platypus import Image
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import pandas as pd
import os
from babel.numbers import format_number
import matplotlib.dates as mdates
from uuid import uuid4 as v4
import seaborn as sns
from matplotlib.ticker import PercentFormatter

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
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None, orientation: str = "vertical", show_xticks: bool = True, show_legend: bool = True, legend_title: str = "Categories", axis_labels: bool = True) -> None:
        super().__init__()

        # Formatear los nombres en el eje y con los conteos
        df[x_col] = df.apply(lambda row: f"{row[x_col]} ({format_number(row[y_col], locale='es_ES')})", axis=1)

        colors = self.get_palette(len(df))
        
        plt.figure(figsize=(12, 8))
        if orientation == "horizontal":
            bars = plt.barh(df[x_col], df[y_col], color=colors)
            if axis_labels:
                plt.xlabel(y_col)
                plt.ylabel(x_col)
        else:
            bars = plt.bar(df[x_col], df[y_col], color=colors)
            if axis_labels:
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            if not show_xticks:
                plt.xticks([])
        
        if title:
            plt.title(title)
        
        if show_legend:
            legend_labels = [f"{label} ({format_number(count, locale='es_ES')})" for label, count in zip(df[x_col], df[y_col])]
            plt.legend(bars, legend_labels, title=legend_title)
        
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

class Historigram(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, freq: str = "1H", rotation: bool = True, title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = 'Count', show_legend: bool = True, grid: bool = True, axis_labels: bool = True) -> None:
        super().__init__()
        
        # Asegurarse de que la columna de fecha sea datetime
        df[x_col] = pd.to_datetime(df[x_col])
        
        # Agrupar los datos según la frecuencia
        df = df.set_index(x_col).resample(freq).sum().reset_index()
        
        colors = ['#1f77b4']  # Paleta de colores simple

        plt.figure(figsize=(18, 10))
        plt.bar(df[x_col], df[y_col], color=colors[0])

        max_count = df[y_col].max()
        max_date = df[x_col][df[y_col].idxmax()]
        max_count_formatted = format_number(max_count, locale='es_ES')

        plt.annotate(f'Max: {max_count_formatted}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color='red')

        # Configurar el eje X
        self.configure_x_axis(plt.gca(), df[x_col])

        if title:
            plt.title(title)
        if axis_labels:
            plt.xlabel(xlabel if xlabel else x_col)
            plt.ylabel(ylabel)
        if show_legend:
            plt.legend([y_col], title='Legend')
        if grid:
            plt.grid(True)
        if rotation:
            plt.xticks(rotation=45)

    def configure_x_axis(self, ax, x_data):
        # Utilizar AutoDateLocator y AutoDateFormatter para manejar el etiquetado de fechas
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        # Submuestreo de etiquetas del eje X
        max_labels = 10  # Número máximo de etiquetas en el eje X
        if len(x_data) > max_labels:
            ticks_to_use = x_data[::len(x_data) // max_labels]
            ax.set_xticks(ticks_to_use)


class Pie(BaseChart):
    def __init__(self, df: pd.DataFrame, category_col: str, value_col: str) -> None:
        super().__init__()
        plt.figure(figsize=(12, 8))
        pie_data = df.groupby(category_col)[value_col].sum()
        colors = self.get_palette(len(pie_data))
        
        pie_data.plot.pie(
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            wedgeprops={'linewidth': 1, 'edgecolor': 'black'}
        )
        plt.title(f'Distribución de {value_col} por {category_col}')
        plt.ylabel('')

class HeatMap(BaseChart):
    def __init__(self, df: pd.DataFrame, index_col: str, columns_col: str, values_col: str, xlabel: str, ylabel: str) -> None:
        super().__init__()

        pivot_df = df.pivot_table(index=index_col, columns=columns_col, values=values_col, aggfunc='sum', fill_value=0)
        plt.figure(figsize=(18, 10))
        sns.heatmap(pivot_df, cmap='coolwarm', annot=True, fmt='d')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

class Box(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str) -> None:
        super().__init__()

        df[y_col] = df[y_col].astype(float)
        plt.figure(figsize=(18, 10))
        sns.boxplot(data=df, x=x_col, y=y_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=90)

class Stacked(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> None:
        super().__init__()

        pivot_df = df.pivot_table(index=x_col, columns=category_col, values=y_col, aggfunc='sum', fill_value=0)
        colors = self.get_palette(len(pivot_df.columns))

        pivot_df.plot(kind='bar', stacked=True, figsize=(18, 10), color=colors)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title=category_col)

class Scatter(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> None:
        super().__init__()

        df[y_col] = df[y_col].astype(float) / 60.0
        plt.figure(figsize=(18, 10))
        sns.scatterplot(data=df, x=x_col, y=y_col, hue=category_col, style=category_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title=category_col)

class Pareto(BaseChart):
    def __init__(self, df: pd.DataFrame, value_col: str, category_col: str) -> None:
        super().__init__()

        df = df.sort_values(by=value_col, ascending=False).reset_index(drop=True)
        df['cum_percentage'] = df[value_col].cumsum() / df[value_col].sum() * 100

        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(df[category_col], df[value_col], color='C0')
        ax2 = ax.twinx()
        ax2.plot(df[category_col], df['cum_percentage'], color='C1', marker='D', ms=7)
        ax2.yaxis.set_major_formatter(PercentFormatter())

        ax.set_xticks(range(len(df[category_col])))
        ax.set_xticklabels(df[category_col], rotation=45, ha='right')
        ax.set_ylabel('Count')
        ax2.set_ylabel('Cumulative Percentage')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

class Bubble(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, size_col: str, color_col: str) -> None:
        super().__init__()

        plt.figure(figsize=(18, 10))
        bubble_size = df[size_col].apply(lambda x: 100 if x == 'critical' else 50)
        
        sns.scatterplot(
            data=df,
            x=x_col,
            y=y_col,
            size=bubble_size,
            hue=color_col,
            palette='coolwarm',
            sizes=(50, 500),
            alpha=0.7,
            edgecolor='k'
        )
        plt.title('Bubble Chart')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45)
        plt.legend(title=color_col)
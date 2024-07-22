from reportlab.platypus import Image
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
import pandas as pd
import os
from babel.numbers import format_number
import matplotlib.dates as mdates
from uuid import uuid4 as v4
import seaborn as sns
import numpy as np
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec

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
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1, transparent=True)
        plt.close()

        return Image(output, width=15.59 * cm, height=8.52 * cm, hAlign="CENTER")

    def get_palette(self, n: int, custom = False):
        if not custom:
            return sns.color_palette('husl', n)
        else:
            base_colors = ["#15a5e4", "#2e9ece", "#4698b8", "#5f91a3", "#788b8d", "#908477", "#a97e61", "#f36a20"]
            n_degradados = 2
            
            colors = []
            for i in range(len(base_colors) - 1):
                cmap = LinearSegmentedColormap.from_list("custom_cmap", [base_colors[i], base_colors[i+1]])
                colors.extend([cmap(j / (n_degradados - 1)) for j in range(n_degradados)])
                
            # Añadir un degradado adicional entre el último y el primero para cerrar el ciclo
            cmap = LinearSegmentedColormap.from_list("custom_cmap", [base_colors[-1], base_colors[0]])
            colors.extend([cmap(j / (n_degradados - 1)) for j in range(n_degradados)])
            
            # Si el número total de colores generados es mayor a n, recortar la lista
            if len(colors) > n:
                return colors[:n]
            else:
                # Generar colores adicionales si es necesario usando 'husl'
                additional_colors = sns.color_palette('husl', n - len(colors))
                return colors + additional_colors

class Bar(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None, orientation: str = "vertical", show_xticks: bool = True, show_legend: bool = True, legend_title: str = "Categories", axis_labels: bool = True, xlabel = "", ylabel = "", xtick_rotation: int = 0) -> None:
        super().__init__()

        # Formatear los nombres en el eje y con los conteos
        df[x_col] = df.apply(lambda row: f"{row[x_col]} ({format_number(row[y_col], locale='es_ES')})", axis=1)

        colors = self.get_palette(len(df))
        
        plt.figure(figsize=(12, 8))
        if orientation == "horizontal":
            bars = plt.barh(df[x_col], df[y_col], color=colors)
            if axis_labels:
                plt.xlabel(ylabel if ylabel != "" else y_col)
                plt.ylabel(xlabel if xlabel != "" else xlabel)
        else:
            bars = plt.bar(df[x_col], df[y_col], color=colors)
            if axis_labels:
                plt.xlabel(xlabel if xlabel != "" else xlabel)
                plt.ylabel(ylabel if ylabel != "" else y_col)
            if not show_xticks:
                plt.xticks([])
        
        if title:
            plt.title(title)
        
        if show_legend:
            legend_labels = [f"{label} ({format_number(count, locale='es_ES')})" for label, count in zip(df[x_col], df[y_col])]
            plt.legend(bars, legend_labels, title=legend_title)
        
        if xtick_rotation != 0 and show_xticks:
            plt.xticks(rotation=xtick_rotation)
        
        plt.tight_layout()

class Line(BaseChart):
    def __init__(self, df: pd.DataFrame, x_col: str, y_col: str, title: Optional[str] = None, category_col: Optional[str] = None, show_legend: bool = True, show_max_annotate: bool = True, axis_labels: bool = True) -> None:
        super().__init__()

        colors = self.get_palette(df[category_col].nunique() if category_col else 1)
        
        plt.figure(figsize=(18, 10))

        if category_col:
            for i, (name, group) in enumerate(df.groupby(category_col)):
                # Formatear los nombres en la leyenda con los conteos
                formatted_name = f"{name} ({format_number(group[y_col].sum(), locale='es_ES')})"
                plt.plot(group[x_col], group[y_col], label=formatted_name, color=colors[i % len(colors)])
                
                # Agregar anotación y línea vertical si el grupo tiene solo un evento
                if group[y_col].sum() == 1:
                    event_date = group[x_col].iloc[0]
                    plt.axvline(x=event_date, color=colors[i % len(colors)], linestyle='--')

                # Anotar el máximo valor
                if show_max_annotate:
                    max_count = group[y_col].max()
                    max_date = group[x_col][group[y_col].idxmax()]
                    plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, random.randint(0, 12)), ha='center', color=colors[i % len(colors)])
        else:
            plt.plot(df[x_col], df[y_col], color=colors[0])
            
            # Agregar anotación y línea vertical si el total de eventos es 1
            if df[y_col].sum() == 1:
                event_date = df[x_col].iloc[0]
                plt.axvline(x=event_date, color=colors[0], linestyle='--')
            
            # Anotar el máximo valor
            if show_max_annotate:
                max_count = df[y_col].max()
                max_date = df[x_col][df[y_col].idxmax()]
                plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[0])

        # Añadir el número total de eventos
        total_events = format_number(df[y_col].sum(), locale='es_ES')
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
    def __init__(self, df: pd.DataFrame, category_col: str, value_col: str, title: Optional[str] = None,
                 explode: Optional[bool] = False, labels: Optional[bool] = True, legend: Optional[bool] = True,
                 min_pct: Optional[float] = 1.0, other_label: Optional[str] = 'Others', legend_title: Optional[str] = None) -> None:
        super().__init__()
        plt.figure(figsize=(12, 8))
        
        # Agrupar datos y calcular porcentajes
        pie_data = df.groupby(category_col)[value_col].sum()
        total = pie_data.sum()
        pie_data_pct = (pie_data / total) * 100
        
        # Filtrar porciones pequeñas
        mask = pie_data_pct >= min_pct
        filtered_data = pie_data[mask]
        other_data = pie_data[~mask]
        other_value = other_data.sum()
        
        if other_value > 0:
            filtered_data[other_label] = other_value
            filtered_pct = pie_data_pct[mask].tolist() + [other_data.sum() / total * 100]
        else:
            filtered_pct = pie_data_pct[mask].tolist()
        
        colors = self.get_palette(len(filtered_data))
        
        # Opcional: Explode para destacar las porciones del pastel
        explode_values = (0.1 if explode else 0) * np.ones(len(filtered_data))
        
        wedges, texts, autotexts = plt.pie(
            filtered_data,
            autopct=lambda p: f'{p:.1f}%' if p >= min_pct else '',
            startangle=140,
            colors=colors,
            explode=explode_values,
            wedgeprops={'linewidth': 1, 'edgecolor': 'black'},
            textprops={'fontsize': 12} if labels else None,
            shadow=False
        )
        
        if title:
            plt.title(title, fontsize=16)
        
        if labels:
            for i, autotext in enumerate(autotexts):
                if filtered_pct[i] >= min_pct:
                    autotext.set_fontsize(10)
                    autotext.set_color('black')
                    
                    # Ajustar la posición de las etiquetas de porcentaje
                    x = autotext.get_position()[0]
                    y = autotext.get_position()[1]
                    # Mover las etiquetas hacia los bordes
                    angle = np.degrees(np.arctan2(y, x))
                    x_edge = 0.6 * np.cos(np.radians(angle))
                    y_edge = 0.6 * np.sin(np.radians(angle))
                    autotext.set_position((x_edge, y_edge))
                    autotext.set_horizontalalignment('center')
                    autotext.set_verticalalignment('center')

        if legend:
            legend_labels = [f'{cat} ({pct:.1f}%)' for cat, pct in zip(filtered_data.index, filtered_pct)]
            legend_title = legend_title if legend_title else category_col
            plt.legend(wedges, legend_labels, title=legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

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

class KPI(BaseChart):
    def __init__(self, kpi_values, kpi_labels, kpi_units=None, layout='centered', rounded=True) -> None:
        if kpi_units is None:
            kpi_units = [""] * len(kpi_values)
        
        # Crear la figura y los ejes
        fig = plt.figure(figsize=(12, 4))
        
        # Determinar la distribución de la cuadrícula
        if layout == 'centered':
            nrows = 1
            ncols = len(kpi_values)
        else:
            # Para layout cuadrado, intentar una distribución cuadrada
            nrows = int(len(kpi_values) ** 0.5)
            ncols = (len(kpi_values) + nrows - 1) // nrows

        # Crear una cuadrícula con GridSpec
        gs = GridSpec(nrows, ncols, figure=fig, wspace=0.1, hspace=0.1) # Reducir wspace y hspace para menos separación
        
        # Obtener colores
        colors = self.get_palette(len(kpi_values))

        # Añadir los cuadros de KPI
        for i, (value, label, unit, color) in enumerate(zip(kpi_values, kpi_labels, kpi_units, colors)):
            row = i // ncols
            col = i % ncols
            ax = fig.add_subplot(gs[row, col])
            ax.axis('off')

            bbox_params = dict(facecolor=color, edgecolor='none', pad=10 if rounded else 30)  # Aumentar pad para cuadros más grandes
            if rounded:
                bbox_params['boxstyle'] = 'round,pad=0.3'  # Ajustar pad para bordes redondeados
            
            ax.text(0.5, 0.6, f"{unit}{value}", ha='center', va='center', fontsize=20, fontweight='bold', color='white', bbox=bbox_params)
            ax.text(0.5, 0.3, label, ha='center', va='center', fontsize=15, color='gray')

    def plot(self):
        output = self._save_chart()
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', transparent=True)
        plt.close()

        return Image(output, width=15.59 * cm, height=7.52 * cm, hAlign="CENTER")

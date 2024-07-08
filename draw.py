import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from uuid import uuid4 as v4
from matplotlib.ticker import PercentFormatter
from typing import TYPE_CHECKING, List
from babel.numbers import format_number

if TYPE_CHECKING:
    from modules.components import Charts

class Draw:
    def __init__(self, charts: 'Charts') -> None:
        self.charts = charts

    def line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str = None) -> str:
        """
        Generate a line chart with optional category grouping.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        category_col (str): The name of the column to categorize the data (optional).

        Returns:
        str: The file path of the saved chart image.
        """
        plt.figure(figsize=(18, 10))
        colors = self._generate_colors(df[category_col].nunique() if category_col else 1)

        if category_col:
            for i, (name, group) in enumerate(df.groupby(category_col)):
                plt.plot(group[x_col], group[y_col], label=f"{name}", color=colors[i % len(colors)])
                max_count = group[y_col].max()
                max_date = group[x_col][group[y_col].idxmax()]
                plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[i % len(colors)])
        else:
            plt.plot(df[x_col], df[y_col], color=colors[0])
            max_count = df[y_col].max()
            max_date = df[x_col][df[y_col].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[0])

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend()
        return self._save_chart()

    def bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, hue_col: str = None, rotate: bool = True) -> str:
        """
        Generate a bar chart with optional hue grouping.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        hue_col (str): The name of the column for hue grouping (optional).
        rotate (bool): Whether to rotate x-axis labels.

        Returns:
        str: The file path of the saved chart image.
        """
        plt.figure(figsize=(12, 8))
        if hue_col:
            sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col, palette=self._generate_colors(len(df[hue_col].unique())))
        else:
            sns.barplot(data=df, x=x_col, y=y_col, palette=self._generate_colors(len(df[x_col].unique())))

        if rotate:
            plt.xticks(rotation=45, ha='right')

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        return self._save_chart()

    def histogram(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str = None, legend: bool = True) -> str:
        """
        Generate a histogram chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        category_col (str): The name of the column to categorize the data (optional).

        Returns:
        str: The file path of the saved chart image.
        """
        plt.figure(figsize=(18, 10))
        colors = self._generate_colors(df[category_col].nunique() if category_col else 1)

        if category_col:
            for i, (name, group) in enumerate(df.groupby(category_col)):
                plt.plot(group[x_col], group[y_col], label=f"{name}", color=colors[i % len(colors)])
                max_count = group[y_col].max()
                max_date = group[x_col][group[y_col].idxmax()]
                plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[i % len(colors)])
        else:
            plt.bar(df[x_col], df[y_col], color=colors[0])
            max_count = df[y_col].max()
            max_date = df[x_col][df[y_col].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[0])

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        if legend: plt.legend()
        return self._save_chart()

    def stacked_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> str:
        """
        Generate a stacked bar chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        category_col (str): The name of the column to categorize the data.

        Returns:
        str: The file path of the saved chart image.
        """
        pivot_df = df.pivot_table(index=x_col, columns=category_col, values=y_col, aggfunc='sum', fill_value=0)
        colors = self._generate_colors(len(pivot_df.columns))

        pivot_df.plot(kind='bar', stacked=True, figsize=(18, 10), color=colors)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title=category_col)
        return self._save_chart()

    def heatmap(self, df: pd.DataFrame, index_col: str, columns_col: str, values_col: str, xlabel: str, ylabel: str) -> str:
        """
        Generate a heatmap chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        index_col (str): The name of the column to be used for the index (y-axis).
        columns_col (str): The name of the column to be used for the columns (x-axis).
        values_col (str): The name of the column to be used for the values.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.

        Returns:
        str: The file path of the saved chart image.
        """
        pivot_df = df.pivot_table(index=index_col, columns=columns_col, values=values_col, aggfunc='sum', fill_value=0)
        plt.figure(figsize=(18, 10))
        sns.heatmap(pivot_df, cmap='coolwarm', annot=True, fmt='d')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        return self._save_chart()

    def scatter_chart(self, df: pd.DataFrame, x_col: str, y_col: str, category_col: str) -> str:
        """
        Generate a scatter plot chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        category_col (str): The name of the column to categorize the data.

        Returns:
        str: The file path of the saved chart image.
        """
        df[y_col] = df[y_col].astype(float) / 60.0

        plt.figure(figsize=(18, 10))
        sns.scatterplot(data=df, x=x_col, y=y_col, hue=category_col, style=category_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.legend(title=category_col)
        return self._save_chart()

    def box_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> str:
        """
        Generate a box plot chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.

        Returns:
        str: The file path of the saved chart image.
        """
        df[y_col] = df[y_col].astype(float)

        plt.figure(figsize=(18, 10))
        sns.boxplot(data=df, x=x_col, y=y_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=90)
        return self._save_chart()

    def pie_chart(self, df: pd.DataFrame, category_col: str, value_col: str) -> str:
        """
        Generate a pie chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        category_col (str): The name of the column to categorize the data.
        value_col (str): The name of the column to be used for the values.

        Returns:
        str: The file path of the saved chart image.
        """
        plt.figure(figsize=(12, 8))
        pie_data = df.groupby(category_col)[value_col].sum()
        colors = self._generate_colors(len(pie_data))
        
        pie_data.plot.pie(
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            wedgeprops={'linewidth': 1, 'edgecolor': 'black'}
        )
        plt.title(f'Distribución de {value_col} por {category_col}')
        plt.ylabel('')
        return self._save_chart()

    def pareto_chart(self, df: pd.DataFrame, value_col: str, category_col: str) -> str:
        """
        Generate a Pareto chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        value_col (str): The name of the column to be used for the values.
        category_col (str): The name of the column to categorize the data.

        Returns:
        str: The file path of the saved chart image.
        """
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
        return self._save_chart()

    def bubble_chart(self, df: pd.DataFrame, x_col: str, y_col: str, size_col: str, color_col: str) -> str:
        """
        Generate a bubble chart.

        Parameters:
        df (pd.DataFrame): The input data frame containing the data to plot.
        x_col (str): The name of the column to be used for the x-axis.
        y_col (str): The name of the column to be used for the y-axis.
        size_col (str): The name of the column to be used for bubble size.
        color_col (str): The name of the column to be used for bubble color.

        Returns:
        str: The file path of the saved chart image.
        """
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
        return self._save_chart()

    def _generate_colors(self, n: int) -> List[str]:
        """
        Generate a list of colors for plotting.

        Parameters:
        n (int): The number of unique colors needed.

        Returns:
        List[str]: A list of color codes.
        """
        base_colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8', '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']
        if n <= len(base_colors):
            return base_colors[:n]
        else:
            additional_colors = sns.color_palette('husl', n - len(base_colors))
            return base_colors + additional_colors

    def _save_chart(self) -> str:
        """
        Save the current matplotlib chart to a file.

        Returns:
        str: The file path of the saved chart image.
        """
        output = os.path.realpath(f"./output/charts/{v4()}.png")
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output), 0o777, True)
        plt.savefig(output, format='png', dpi=400, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        return output

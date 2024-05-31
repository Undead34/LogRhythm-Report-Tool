import os
import numpy as np
import pandas as pd
from uuid import uuid4 as v4

import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns
import seaborn.objects as so


class Charts():
    def __init__(self) -> None:
        pass

    def chart_stacked_bar(self, data: pd.DataFrame) -> str:
        # Definir los colores para las barras
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        # Crear la gráfica de barras apiladas
        data.plot(kind='bar', stacked=True, figsize=(
            18, 10), width=0.8, color=colors)

        # Personalizar la gráfica
        plt.title(None)
        plt.xlabel(None)
        plt.ylabel(None)
        plt.yscale('log')  # Establecer escala logarítmica en el eje Y

        plt.xticks(rotation=90, fontsize='small')
        plt.legend(title='Tipo de Alarma', loc='upper left')

        output = os.path.realpath(f"./output/charts/{v4()}.png")

        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)

        plt.savefig(output, format='png', dpi=400,
                    bbox_inches='tight', pad_inches=0.1)

        # plt.show()

        return output

    def chart_histogram(self, data: pd.DataFrame) -> str:
        # Ajustar el tamaño de la figura
        plt.figure(figsize=(18, 10))

        # Definir la paleta de colores
        colors = ['#50BBD4', '#4F81A4', '#F9A40C', '#F96611', '#941C2F', '#D7BCE8',
                  '#D7263D', '#464655', '#495159', '#05F140', '#A790A5', '#875C74']

        # Graficar los datos
        for i, (name, group) in enumerate(data.groupby('AlarmName')):
            total_events = group['Counts'].sum()
            color = colors[i % len(colors)]
            plt.plot(group['AlarmDate'], group['Counts'],
                     label=f"{name} - Total: ({total_events})", color=color)

            max_count = group['Counts'].max()
            max_date = group['AlarmDate'][group['Counts'].idxmax()]
            plt.annotate(f'Max: {max_count}', (max_date, max_count), textcoords="offset points", xytext=(
                0, 10), ha='center', color=color)

            # Si la alarma solo ocurrió en un día, dibujar una línea vertical punteada
            if len(group) == 1:
                plt.axvline(x=group['AlarmDate'].iloc[0],
                            color=color, linestyle='dashed')

        # Ajusta los ticks del eje y
        plt.yticks(np.arange(0, data['Counts'].max(), step=300))

        # Ajustar los ticks del eje x
        plt.xticks(pd.date_range(start=data['AlarmDate'].min(
        ), end=data['AlarmDate'].max(), freq='3D'))

        plt.legend()

        output = os.path.realpath(f"./output/charts/{v4()}.png")

        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(output, 0o777, True)

        plt.savefig(output, format='png', dpi=400,
                    bbox_inches='tight', pad_inches=0.1)

        # plt.show()

        return output

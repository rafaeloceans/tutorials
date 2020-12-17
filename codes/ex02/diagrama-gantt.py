#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    diagrama-gantt.py: rotina para gerar um diagrama ou gráfico de Gantt a partir
    de um cronograma pré-estabelecido. Um tutorial pode ser encontrado
    em https://github.com/rdviana/tutorials-python.
"""
__author__ = 'Rafael D. Viana'
__copyright__ = "Copyright 2020, Rafael D. Viana"
__credits__ = ['Viana, R.D.']
__license__ = "Public Domain"
__version__ = "1.0"
__maintainer__ = "Rafael D. Viana"
__email__ = 'ocn.rviana@gmail.com'

"""-------------------------------------------------------------
    IMPORTAÇÃO DE BIBLIOTECAS
-------------------------------------------------------------"""
# Bibliotecas para tabelas
import pandas as pd

# Bibliotecas gráficas
import plotly.express as px

"""-------------------------------------------------------------
    PROGRAMA PRINCIPAL
-------------------------------------------------------------"""
# Faz a leitura do arquivo .xlsx contendo o cronograma de atividades.
df = pd.read_excel("data/cronograma-atividades.xlsx", header=0,
                   dtype={'Atividade': str, 'Data_inicio': str, 'Data_final': str, 'Etapa': str})

# Converte o formato das datas para datetime
df['Data_inicio'] =  pd.to_datetime(df['Data_inicio'], format='%d-%m-%Y')
df['Data_final']  =  pd.to_datetime(df['Data_final'], format='%d-%m-%Y')

# Cria uma sequência de cores customizada para o gráfico
custom_colorscheme = ["#173F5F", "#20639B", "#3CAEA3", "#F6D55C", "#ED553B"]
colorsequence = custom_colorscheme

# Obtêm a lista de atividades da tabela
activity_list = df["Atividade"].tolist()
activity_list = ['<b>'+elem+'</b>' for elem in activity_list] # Estiliza a lista para o formato HTML

# Gerando o gráfico do cronograma: Versão final
fig = px.timeline(df, x_start="Data_inicio", x_end="Data_final", y=activity_list, color="Etapa",
                  color_discrete_sequence=colorsequence, opacity=0.9,
                  width=960, height=500, template="seaborn")
fig.update_yaxes(autorange="reversed")                  # Inverte o eixo vertical.
fig.update_traces(width=0.6)                            # Reduz a altura das barras horizontais
fig.update_xaxes(                                       # Altera a forma que os meses são mostrados no eixo x
    range=["2019-03-01", "2020-03-01"],                 # Selecionamos o intervalo de meses no plot
    dtick="M1",                                         # Interalo de um em um mês (para a cada 3 meses, por exemplo, use M3)
    tickformat="%_m\n%Y")                               # Formato 1, 2, 3...
fig.update_layout(
    xaxis={
        'linecolor':'gray',
        'linewidth': 1.5,
        'showline':True,                                # Adiciona um grid cinza ao background da figura;
        'gridwidth':0.8,
        'gridcolor':'lightgray'},
    yaxis={
        'title':'',
        'tickfont':{'size':14,'color':'dimgray'},
        'ticksuffix':'  ',
        'linecolor':'gray',
        'linewidth': 1.5,
        'showline':True,                                # Adiciona um grid cinza ao background da figura;
        'gridwidth':0.8,
        'gridcolor':'lightgray'},
    legend={                                            # Modifica a barra de legenda
        'orientation':"h",
        'yanchor':"bottom",
        'y':-0.2,
        'xanchor':"right",
        'x':1},
    title={                                             # Adiciona um título à figura
        'text': "<b>Cronograma de atividades</b>",
        'y': 0.93,
        'x': 0.35,
        'xanchor': 'left',
        'yanchor': 'bottom',
        'font': {'size': 24, 'color': "dimgray"}},
    plot_bgcolor='rgba(0,0,0,0)')                       # Modifica a cor do background do gráfico para branco

# Salva o cronograma na pasta figs
fig.write_image("figs/cronograma-projeto.png", scale=1)

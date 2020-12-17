#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    pesquisa-scopus.py: rotina para acesso e pesquisa na base de dados Scopus
    e extração de informações dos manuscritos na base. Um tutorial pode ser encontrado
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
# Bibliotecas para tabelas e operações numéricas
import csv
import numpy as np
import pandas as pd

# Bibliotecas Genéricas/OS
from datetime import datetime

# Bibliotecas gráficas
import matplotlib.pyplot as plt
import seaborn as sns

# Biblioteca para acessar a Base de Dados Scopus
from pybliometrics.scopus import config, AbstractRetrieval, ScopusSearch
from pybliometrics.scopus.exception import Scopus404Error, Scopus429Error

"""-------------------------------------------------------------
    CONFIGURAÇÃO GRÁFICA
-------------------------------------------------------------"""
# Configura o formato de exibição gráfica da biblioteca Seaborn
sns.set_context('paper')
sns.set_theme(style="whitegrid")

SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 20

plt.rc('font', size=BIGGER_SIZE)         # tamanho da fonte padrão
plt.rc('axes', titlesize=SMALL_SIZE)     # tamanho da fonte do título dos eixos
plt.rc('axes', labelsize=MEDIUM_SIZE)    # tamanho da fonte dos marcadores dos eixos x e y
plt.rc('xtick', labelsize=SMALL_SIZE)    # tamanho da fonte dos marcadores do eixo-x
plt.rc('ytick', labelsize=SMALL_SIZE)    # tamanho da fonte dos marcadores do eixo-y
plt.rc('legend', fontsize=SMALL_SIZE)    # tamanho da fonte da legenda
plt.rc('figure', titlesize=BIGGER_SIZE)  # tamanho da fonte do título da figura

"""-------------------------------------------------------------
    FUNÇÕES LOCAIS
-------------------------------------------------------------"""
# Função para coletar informações dos artigos.
def coletar_artigos(eids_documentos, api_view):
    # Inicializa uma lista de dados vazia {data}; para cada entrada na lista de artigos obtidos
    # cria um dicionário para armazenar as informações específicas sobre o artigo e
    # armazena nessa lista
    data = []
    for key in eids_documentos:
        record = {}
        error = True
        while error:
            try:
                paper = AbstractRetrieval(key, id_type="eid", view=api_view, refresh=True)
                error = False
                # Informações básicas.
                record["id"] = paper.identifier
                record["doi"] = paper.doi
                record["eid"] = paper.eid
                record["pii"] = paper.pii
                record["pubmed_id"] = paper.pubmed_id
                record["titulo"] = paper.title
                record["resumo"] = paper.abstract
                record["descricao"] = paper.description
                record["data_publicacao"] = datetime.strptime(paper.coverDate, "%Y-%m-%d").date() \
                    if paper.coverDate else None
                record["numero_citacao"] = paper.citedby_count
                record["idioma"] = paper.language
                record["tipo_publicacao"] = paper.aggregationType
                record["tipo_fonte"] = paper.srctype
                record["palavras_chaves"] = tuple(paper.authkeywords) if paper.authkeywords else None
                record["termos_indice"] = tuple(paper.idxterms) if paper.idxterms else None
                record["issn"] = paper.issn

                try:
                    record["isbn"] = " ".join(paper.isbn) if type(paper.isbn) == tuple else paper.isbn
                except TypeError:
                    record["isbn"] = None

                # Informações sobre a Conferencia e/ou Revista.
                record["conf_loc"] = paper.conflocation
                record["conferencia_nome"] = paper.confname
                record["revista_nome"] = paper.publicationName
                record["revista_ender"] = paper.publisheraddress
                record["titulo_ed"] = paper.issuetitle
                record["publis"] = paper.publisher

                # Informações sobre afiliação.
                record["affiliacoes"] = tuple(
                    [{"id": affil.id if affil and affil.id else None,
                      "affiliacao": affil.name if affil and affil.name else None,
                      "pais": affil.country if affil and affil.country else None}
                     for affil in paper.affiliation]) if paper.affiliation else None

                # Informações sobre os autores.
                record["autores"] = tuple(
                    [{"id": author.auid if author and author.auid else None,
                      "nome": "{} {}".format(author.given_name, author.surname) \
                          if author and author.given_name and author.surname else None}
                     for author in paper.authors]) if paper.authors else None

                record["autores_affil"] = tuple(
                    [{"id": author.auid if author and author.auid else None,
                      "nome": "{} {}".format(author.given_name, author.surname) \
                          if author and author.given_name and author.surname else None,
                      "affil_id": author.affiliation_id if author and author.affiliation_id else None,
                      "affiliacao": author.organization if author and author.organization else None,
                      "pais": author.country if author and author.country else None}
                     for author in paper.authorgroup]) if paper.authorgroup else None

                # Informações sobre referencias.
                record["ref_count"] = paper.refcount if paper.refcount else None
                record["references"] = tuple([{"id": ref.id if ref and ref.id else None,
                                               "titulo": ref.title if ref and ref.title else None,
                                               "doi": ref.doi if ref and ref.doi else None,
                                               "autores": ref.authors if ref and ref.authors else None}
                                              for ref in paper.references]) if paper.references else None

            except Scopus404Error:
                record["id"] = key
                print(key)
                error = False
            except Scopus429Error:
                config["Authentication"]["APIKey"] = _keys.pop()
        data.append(record)

    df = pd.DataFrame(data)

    return df

"""-------------------------------------------------------------
    PROGRAMA PRINCIPAL
-------------------------------------------------------------"""
# Configurando a chave de acesso na API da Scopus.
_keys = ["chave de acesso aqui"] # <-- modifique aqui adicionando sua chave de acesso
config["Authentication"]["APIKey"] = _keys.pop()
api_view = "META"

# Descomente a próxima linha para configurar a chave de acesso durante a primeira execução do programa.
# create_config()

# Configurando os critérios de pesquisa.
query = 'TITLE-ABS-KEY("protected area" OR "conservation" OR "ecology" OR "marine protected" OR "national forest")' \
        ' AND TITLE-ABS-KEY("remote sensing" OR "earth observation" OR "Landsat" OR "Lidar" OR "MODIS" OR "Radar")' \
        ' AND TITLE-ABS-KEY("Brazil" OR "Brasil")' \
        ' AND PUBYEAR BEF 2021 AND PUBYEAR AFT 1999' \
        ' AND LANGUAGE(english OR portuguese)'

# Cria um objeto de pesquisa ScopusSearch contendo as informações para busca.
scopus = ScopusSearch(query, max_entries=None, subscriber=False, verbose=True)

# Retorna o número de registros coletados pela API.
print("Número total de publicações: {}.".format(scopus.get_results_size()))

# Obtêm uma lista contendo todos os identificadores digitais (EID) resgatados da API durante a busca.
eids_documentos = scopus.get_eids()

# Coleta as informações sobre os artigos, a partir dos EID e da função auxiliar.
df = coletar_artigos(eids_documentos, api_view)

# Armazena todas as entradas em um arquivo .csv, para consulta posterior
df.to_csv("data/resultado_pesquisa_scopus.csv", index=False, quoting=csv.QUOTE_ALL)

"""-------------------------------------------------------------
    EXTRA: Plotando o histórico temporal de publicações
-------------------------------------------------------------"""
# Converte o tipo de dado da coluna "data_publicacao" para datetime
datetimes = pd.to_datetime(df["data_publicacao"])       # realiza a conversão utilizando a função pd.to_datetime()
df["data_publicacao"] = datetimes                       # substitui o conteúdo original da coluna "data_publicacao"
df["ano_publicacao"] = df["data_publicacao"].dt.year    # Criamos uma nova coluna para armazenar apenas o ano da publicação

# Filtra a base intelectual para conter apenas os trabalhos publicados em periódicos (categoria Journal)
tipo_publ = df["tipo_publicacao"].astype(str) == "Journal"   # O método .astype(str) converte o conteúdo da coluna em string
df = df[tipo_publ].reset_index(drop=True)

# Conta o número de publicações por ano de publicação
pub    = df.groupby("ano_publicacao").size()
pub    = pub.values
df_pub = df.drop_duplicates(subset="ano_publicacao").assign(Count=np.flipud(pub))

# Cria uma nova tabela a partir da contagem de publicações e reorganiza por ordem crescente dos anos
df_plot = df_pub[["ano_publicacao","Count"]].copy()
df_plot = df_plot.sort_values(by=['ano_publicacao']).reset_index(drop=True)

# Cria o plot
fig, ax = plt.subplots(figsize=(14,7))
sns.barplot(ax=ax, x="ano_publicacao", y="Count", data=df_plot, palette="Reds_d")
sns.despine(ax=ax)   # Remove os eixos da direita e superior no gráfico
plt.xticks(rotation=90)
plt.xlabel("Ano de publicação", labelpad=20)
plt.ylabel("", labelpad=10) # Remove label do eixo vertical
plt.title("Número de publicações integrando sensoriamento remoto e áreas de conservação\nno Brasil por ano, no período de 2000 à 2020", fontsize=18)
ax.annotate("Fonte: Base de dados Scopus", xy=(0.08, 0.82), size=14,  style='italic', xycoords='figure fraction')
# Descomente a linha abaixo para salvar a figura
#plt.savefig('figs/total_publicacoes_ano.png', dpi=96, bbox_inches='tight', pad_inches=0.2)
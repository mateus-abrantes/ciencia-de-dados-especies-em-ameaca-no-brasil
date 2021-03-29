# Instalação do Plotly
!pip install Plotly==4.12

# Instalação do Dash
!pip install dash
!pip install dash-html-components
!pip install dash-core-components
!pip install dash-table
# Pacotes Python Pandas e Plotly
import numpy as np
import pandas as pd
import plotly.express as px
# Pacotes para criação de processos para suportar o serviço URL externo do Ngrok
import os.path
import sys, json
import requests
import subprocess

# Pacotes de tratamento de URL
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from collections import namedtuple
# Definição da função de Download do Ngrok
def download_ngrok():
    if not os.path.isfile('ngrok'):
        !wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
        !unzip -o ngrok-stable-linux-amd64.zip
    pass
# Criação de um Túnel entre uma aplicação no Colab e uma URL externa no Ngrok
# Função para pegar a referência nesse túnel

Response = namedtuple('Response', ['url', 'error'])

def get_tunnel():
    try:
        Tunnel = subprocess.Popen(['./ngrok','http','8050'])

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)

        res = session.get('http://localhost:4040/api/tunnels')
        res.raise_for_status()

        tunnel_str = res.text
        tunnel_cfg = json.loads(tunnel_str)
        tunnel_url = tunnel_cfg['tunnels'][0]['public_url']

        return Response(url=tunnel_url, error=None)
    except RequestException as e:
        return Response(url=None, error=str(e))

download_ngrok()

dados = pd.read_csv('https://raw.githubusercontent.com/talesjoabe/especiesAmeacadas/main/dados_tratados.csv')
dados.head()

dados.drop('Unnamed: 0',axis=1, inplace=True)

dados.head()

dados['Estados de Ocorrência'].str.contains('^F.*')

lista_ameacas = []
ameacas = ''

for i in dados.get('Principais Ameaças'):
  ameacas = i.split(',')
  for ameaca in ameacas:
    if ameaca not in lista_ameacas and ameaca!='':
      lista_ameacas.append(ameaca)

print(lista_ameacas)

lista_biomas = []
biomas = ''

for i in dados.get('Bioma'):
  biomas = i.split(',')
  for bioma in biomas:
    if bioma not in lista_biomas and bioma!='':
      lista_biomas.append(bioma)

print(lista_biomas)

dados['Estados de Ocorrência'] = dados['Estados de Ocorrência'].astype(str)

lista = []
ufs = ''

for i in dados.get('Estados de Ocorrência'):
  ufs = i.split(',')
  for uf in ufs:
    if uf not in lista and uf!='':
      lista.append(uf)

print(lista)
print(len(lista))

# Arquivo de utilitários

%%writefile utils.py
import plotly.graph_objects as go
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import requests
import numpy as np


def generate_bar_chart(df, column, filter_columns, title, xaxis=dict(), yaxis=dict(), legend={'x': 1, 'y': 1}, orientation='h', barmode='stack'):
  fig = go.Figure()
  for key, values_list in filter_columns.items():
    for item in values_list:
      df_filtered = df[df[key] == item]
      axis = df_filtered[column].value_counts()
      fig.add_trace(
        go.Bar(
          x=axis.values if orientation == 'h' else axis.index,
          y=axis.index if orientation == 'h' else axis.values,
          name=item,
          orientation=orientation
        )
      )
      
  fig.update_layout(barmode=barmode, title_text=title, xaxis=xaxis, yaxis=yaxis, legend={**legend, 'bgcolor': 'rgba(255, 255, 255, 0)', 'bordercolor': 'rgba(255, 255, 255, 0)'})
  return fig


#cloud_mask = np.array(Image.open(requests.get('https://lh3.googleusercontent.com/proxy/xxQLBFLx2RC-OQ7gn-D7UUACbTUnJQlJCMRyeU4nDGYZXafHeXMPpZx5IF021TT51ajfwUoQf8ZM5f_3cVIVayOL8qHXNWUVl1QmfFK1tdM1BSQpXKDgwVogeTT0ZWY2o8BQzvs4xstzhQ4ggw', stream=True).raw))

def plot_wordcloud(data, shape):
  d = {a: x for a, x in data.values}
  wc = WordCloud(background_color='white', width=750, height=400, scale=1.0)
  wc.fit_words(d)
  return wc.to_image()


def add(a, b, c, d, e):
    return a + b + c + d + e


categoria = {
    'VU': 1,
    'EN': 2,
    'CR': 3
}


nivel_protecao = {
    0: 5,
    1: 4,
    2: 3,
    3: 2,
    4: 1,
    5: 0
}

protecao = {
    'Sim': 0,
    'Não': 1
}


exclusiva = {
    'Sim': 1,
    'Não': 0,
    'Informação não disponível': 0
}

# Geração do programa exemplo_dash_4.py

%%writefile exemplo_dash_4.py
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import *
from io import BytesIO
import base64

dados = pd.read_csv('https://raw.githubusercontent.com/talesjoabe/especiesAmeacadas/main/dados_tratados.csv')
dados_separados = pd.read_csv('https://raw.githubusercontent.com/talesjoabe/especiesAmeacadas/main/dados_separados.csv') 
dados_biomas = pd.read_csv('https://raw.githubusercontent.com/talesjoabe/especiesAmeacadas/main/dados_biomas.csv')

dados_ameacas = dados
dados_ameacas.rename(columns={"Principais Ameaças": "Principais_ameacas"}, inplace = True)
dados_ameacas = dados_ameacas.assign(Principais_ameacas=dados['Principais_ameacas'].str.split(",")).explode('Principais_ameacas')

dados_ameacas_qtd = dados.set_index(dados['Espécie (Simplificado)'])
dados_ameacas_qtd['qtd_ameacas'] = dados_ameacas['Espécie (Simplificado)'].value_counts()
dados_ameacas_qtd['total_ameacas'] = dados_ameacas_qtd.apply(
    lambda row: add(
        row['qtd_ameacas'],
        # categoria[row['Sigla Categoria de Ameaça']],
        nivel_protecao[row['Nível de Proteção na Estratégia Nacional']],
        protecao[row['Presença em Áreas Protegidas'] if row['Presença em Áreas Protegidas'] in ['Sim', 'Não'] else 'Sim'],
        protecao[row['Plano de Ação Nacional para Conservação (PAN)']],
        exclusiva[row['Espécie exclusiva do Brasil']]
    ), axis = 1
)
ameacas_fauna = dados_ameacas_qtd[dados_ameacas_qtd['Fauna/Flora'] == 'Fauna']
ameacas_flora = dados_ameacas_qtd[dados_ameacas_qtd['Fauna/Flora'] == 'Flora']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig1 = go.Figure(data=[go.Pie(labels=dados['Espécie exclusiva do Brasil'].unique(), values=dados['Espécie exclusiva do Brasil'].value_counts(), hole=.3)])
fig1.update_layout(title_text="Espécies exclusivas no Brasil")

fig2 = generate_bar_chart(
  dados,
  "Grupo",
  {"Espécie exclusiva do Brasil": ["Sim", "Não", "Informação não disponível"]},
  "Perfil dos Grupos em relação a exclusividade no Brasil",
  xaxis={'title': 'Quantidade de espécies'},
  yaxis={'title': 'Grupos'},
  legend={'x': 0.7, 'y': 1}
)
fig3 = generate_bar_chart(
  dados_biomas,
  "Bioma",
  {"Espécie exclusiva do Brasil": ["Sim", "Não", "Informação não disponível"]},
  "Perfil dos Biomas em relação a exclusividade no Brasil",
  xaxis={'title': 'Quantidade de espécies'},
  yaxis={'title': 'Biomas'},
  legend={'x': 0.7, 'y': 1}
)

fig4 = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Sim', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index, 
                              values=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Sim', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(), hole=.4)])
fig4.update_layout(title_text="Existência de um Plano Nacional para Conservação (PAN) <br> dentre as espécies exclusivas no Brasil", colorway=['#EF553B', '#636EFA'])


fig5 = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Não', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index, 
                              values=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Não', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(),hole=.4)])
fig5.update_layout(title_text="Existência de um Plano Nacional para Conservação (PAN) <br> dentre as espécies não exclusivas no Brasil" , colorway=['#636EFA', '#EF553B'], legend_traceorder = 'reversed')


app.layout = html.Div([html.Div(children=[
      html.H1(children='DCA01131 - CIÊNCIA DE DADOS'),
      html.H2(children='Análise das espécies ameaçadas no Brasil'),
      html.Div(children=['1. Isaac Gomes', html.Br(), '2. Mateus Abrantes', html.Br(), '3. Tales Joabe']),
  ]),

  html.Div(children= dcc.Graph(
    id='item-1',
    figure=fig1
  )), 

  html.Div(children= [ 
    html.Div(children= dcc.Graph(
      id='item-2',
      figure=fig2
    ), className='six columns'), 
    html.Div(dcc.Graph(
      id='item-3',
      figure=fig3
    ), className='six columns'),    
  ], className='row'),

  html.Div(children= [ 
    html.Div(children= dcc.Graph(
      id='item-4',
      figure=fig4
    ), className='six columns'), 
    
    html.Div(dcc.Graph(
      id='item-5',
      figure=fig5
    ), className='six columns'),  

  ], className='row'),

  html.Div(children= [ 
    html.Center(html.Div(children=['Espécies da Fauna com mais diversidade de ameaças'], style={'font-size': '20px', 'color': '#2a3f5f'}), className='six columns'), 
    html.Center(html.Div(children=['Espécies da Flora com mais diversidade de ameaças'], style={'font-size': '20px', 'color': '#2a3f5f'}), className='six columns'),    
  ], className='row'),

  html.Div(children= [ 
    html.Center(html.Div(children=[
      html.Img(id="image_wc_fauna"),
    ], className='six columns')), 
    html.Center(html.Div(children=[
      html.Img(id="image_wc_flora"),
    ], className='six columns')),    
  ], className='row'),

#   html.Div([
#             dcc.Dropdown(
#                 id='xaxis-column',
#                 options=[{'label': i, 'value': i} for i in dados_biomas['Bioma'].value_counts().index],
#                 value = 'Cerrado'
#             ),
#         ]),
  
#     html.Div([
#         dcc.Graph(id='the_graph')
#     ]),
])

@app.callback(Output('image_wc_fauna', 'src'), [Input('image_wc_fauna', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=ameacas_fauna[['Espécie (Simplificado)', 'total_ameacas']], shape='fauna').save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(Output('image_wc_flora', 'src'), [Input('image_wc_flora', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=ameacas_flora[['Espécie (Simplificado)', 'total_ameacas']], shape='flora').save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id= 'xaxis-column', component_property='value')]
)
def update_graph(xasis_column_name):
    fig_teste = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Bioma'] == xasis_column_name, 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index, 
                          values=dados_biomas.loc[dados_biomas['Bioma'] == xasis_column_name, 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(),hole=.4)])
    fig_teste.update_layout(title_text="Existência de um Plano Nacional para Conservação (PAN) <br> dentre as espécies não exclusivas no Brasil" , colorway=['#636EFA', '#EF553B'], legend_traceorder = 'reversed')
    return (fig_teste)

if __name__ == '__main__':
    app.run_server(debug=True)
    
dados_biomas['Bioma'].value_counts()

retorno = get_tunnel()
print(retorno)  # Para podermos saber o endereço da URL da Aplicação
!python exemplo_dash_4.py

dados_biomas = pd.read_csv('https://raw.githubusercontent.com/talesjoabe/especiesAmeacadas/main/dados_biomas.csv') 

dados_biomas.loc[(dados_biomas['Espécie exclusiva do Brasil'] == 'Sim') &  (dados_biomas['Plano de Ação Nacional para Conservação (PAN)'] == 'Sim'), 'Bioma'].value_counts().index


['Mata Atlântica', 'Cerrado', 'Caatinga' , 'Amazônia', 'Pampa', 'Marinho', 'Pantanal', 'Ilha oceânica']

dados_biomas.loc[(dados_biomas['Espécie exclusiva do Brasil'] == 'Sim') &  (dados_biomas['Espécie exclusiva do Brasil'] == 'Sim'), 'Bioma'].value_counts()

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import json
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
],)

estados = pd.read_csv("./date/especies_ameacadas_por_estados.csv")
biomas = pd.read_csv("./date/especies_ameacadas_por_biomas.csv")
geojson_estados = json.load(open('./assets/Brasil.json'))
geojson_biomas = json.load(open('./assets/biomas_brasil.json'))
estados.reset_index(inplace=True)
biomas.reset_index(inplace=True)

map_graph = html.Div([

    html.H5("Espécies ameaçadas por Estados",
            style={'text-align': 'center'}),

    dcc.Dropdown(id="estados_select",
                 options=[
                     {"label": "Quantidade total de espécies ameaçadas",
                      "value": "Espécies ameaçadas"},
                     {"label": "Fauna", "value": "Fauna espécies ameaçadas"},
                     {"label": "Flora", "value": "Flora espécies ameaçadas"},
                     {"label": "Angiospermas",
                      "value": "Angiospermas espécies ameaçadas"},
                     {"label": "Anfíbios", "value": "Anfíbios espécies ameaçadas"},
                     {"label": "Aves", "value": "Aves espécies ameaçadas"},
                     {"label": "Briófitas",
                      "value": "Briófitas espécies ameaçadas"},
                     {"label": "Gimnospermas",
                      "value": "Gimnospermas espécies ameaçadas"},
                     {"label": "Invertebrados aquaticos",
                      "value": "Invertebrados aquaticos espécies ameaçadas"},
                     {"label": "Invertebrados terrestres",
                      "value": "Invertebrados terrestres espécies ameaçadas"},
                     {"label": "Mamiferos",
                      "value": "Mamiferos espécies ameaçadas"},
                     {"label": "Peixes continentais",
                      "value": "Peixes continentais espécies ameaçadas"},
                     {"label": "Peixes marinhos",
                      "value": "Peixes marinhos espécies ameaçadas"},
                     {"label": "Pteridofitas",
                      "value": "Pteridofitas espécies ameaçadas"},
                     {"label": "Repteis", "value": "Repteis espécies ameaçadas"}],
                 multi=False,
                 clearable=False,
                 value="Espécies ameaçadas",
                 ),
    dcc.Graph(id='my_bee_map', figure={}),
])


@app.callback(
    Output(component_id='my_bee_map', component_property='figure'),
    [Input(component_id='estados_select', component_property='value')]
)
def update_graph(option_slctd):
    dff = estados.copy()

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson=geojson_estados,
        locations='Estado_de_Ocorrencia',
        scope="south america",
        color=option_slctd,
        hover_data=['Estado_de_Ocorrencia'],
        template='plotly_dark',
    )
    return fig


map_biomas = html.Div([
    html.Br(),
    html.H5("Espécies ameaçadas por Biomas",
            style={'text-align': 'center'}),
    dcc.Dropdown(id="biomas_select",
                 options=[
                     {"label": "Quantidade total de espécies ameaçadas",
                      "value": "Espécies ameaçadas"},
                     {"label": "Angiospermas",
                      "value": "Angiospermas espécies ameaçadas"},
                     {"label": "Anfíbios", "value": "Anfíbios espécies ameaçadas"},
                     {"label": "Aves", "value": "Aves espécies ameaçadas"},
                     {"label": "Briófitas",
                      "value": "Briófitas espécies ameaçadas"},
                     {"label": "Gimnospermas",
                      "value": "Gimnospermas espécies ameaçadas"},
                     {"label": "Invertebrados aquaticos",
                      "value": "Invertebrados aquaticos espécies ameaçadas"},
                     {"label": "Invertebrados terrestres",
                      "value": "Invertebrados terrestres espécies ameaçadas"},
                     {"label": "Mamiferos",
                      "value": "Mamiferos espécies ameaçadas"},
                     {"label": "Peixes continentais",
                      "value": "Peixes continentais espécies ameaçadas"},
                     {"label": "Peixes marinhos",
                      "value": "Peixes marinhos espécies ameaçadas"},
                     {"label": "Pteridofitas",
                      "value": "Pteridofitas espécies ameaçadas"},
                     {"label": "Repteis", "value": "Repteis espécies ameaçadas"}],
                 multi=False,
                 clearable=False,
                 value="Espécies ameaçadas",
                 ),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='my_bee_map2', figure={})),
            dbc.Col(dcc.Graph(id='my_bee_map3', figure={})),
        ]
    ),

])
# Connect the Plotly graphs with Dash Components


@ app.callback(
    [Output(component_id='my_bee_map2', component_property='figure'),
     Output(component_id='my_bee_map3', component_property='figure')],
    [Input(component_id='biomas_select', component_property='value')]
)
def update_graph(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)

    dff = biomas.copy()

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson=geojson_biomas,
        locations='Bioma',
        scope="south america",
        color=option_slctd,
        hover_data=['Bioma'],
        template='plotly_dark',
    )

    fig_bar_dados_biomas = px.bar(dff, y=option_slctd, x='Bioma', template='plotly_dark',
                                  text=option_slctd, color=option_slctd, color_continuous_scale='Reds')
    fig_bar_dados_biomas.update_traces(
        texttemplate='%{text:.2s %}', textposition='outside')
    fig_bar_dados_biomas.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide')
    fig_bar_dados_biomas.update_layout(
        xaxis={'categoryorder': 'total ascending'})

    return fig, fig_bar_dados_biomas

# satellite_dropdown = dcc.Dropdown(
#     id="satellite-dropdown-component",
#     options=[
#         {"label": "H45-K1", "value": "h45-k1"},
#         {"label": "L12-5", "value": "l12-5"},
#     ],
#     clearable=False,
#     value="h45-k1",
# )


satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=["DCA01131", html.Br(), "CIÊNCIA DE DADOS"]
)

satellite_title = html.H1(
    id="satellite-name", children="Análise das espécies ameaçadas no Brasil")

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=["1. Isaac Gomes", html.Br(), "2. Mateus Abrantes", html.Br(), "3. Tales Joabe"]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        satellite_dropdown_text,
        # html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Div(id="panel-side-text",
                 children=[satellite_title, satellite_body]),
    ],
)


main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        map_graph,
        map_biomas,
    ],
)

app.layout = html.Div([
    html.Div(
        id="root",
        children=[
            side_panel_layout,
            main_panel_layout,
        ],
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)

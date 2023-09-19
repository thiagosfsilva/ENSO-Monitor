from dash import Dash, dcc
import dash_bootstrap_components as dbc
from plot_level import plot_level
from pandas import read_pickle

# Generate water level plot
fig_level = plot_level()
updated = read_pickle('data/upDate.pkl')

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],)
server = app.server

app.layout = dbc.Container([
    dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(f'Last updated on / Atualizado em {updated}', href="#")),
    ],
    brand="Monitor ENSO El Ninõ 2023 -  Fonte Boa",
    brand_href="#",
    color="primary",
    dark=True,
    ),
    #dbc.Row([
    #    dbc.Col([           
    #html.H1(children='ENSO 2003 drought monitor', style={'textAlign':'center'}),
    #html.H2(children=f'Last updated on {updated}', style={'textAlign':'center'}),
    #html.Hr(),
    #        ])
    #    ]),
    dbc.Row(
    dcc.Graph(id='fig-level', figure=fig_level,  style={'aspect-ratio': '21 / 10'}),
    )
],
fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
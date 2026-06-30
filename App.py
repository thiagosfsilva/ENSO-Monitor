from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from plot_level import plot_level
from pandas import read_pickle

figs    = plot_level()
updated = read_pickle('data/levels/upDate.pkl')

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(
                f'Last updated / Atualizado em {updated.iloc[0, 0]}', href='#'
            )),
        ],
        brand='Monitor ENSO - Niveis do Rio Amazonas',
        brand_href='#',
        color='primary',
        dark=True,
    ),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='fig-12351000', figure=figs['12351000'],
                      style={'aspect-ratio': '4/3'}),
            width=6
        ),
        dbc.Col(
            dcc.Graph(id='fig-11400000', figure=figs['11400000'],
                      style={'aspect-ratio': '4/3'}),
            width=6
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='fig-14990000', figure=figs['14990000'],
                      style={'aspect-ratio': '4/3'}),
            width=6
        ),
        dbc.Col(
            dcc.Graph(id='fig-17050001', figure=figs['17050001'],
                      style={'aspect-ratio': '4/3'}),
            width=6
        ),
    ]),
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)

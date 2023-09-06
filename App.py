from dash import Dash, dcc
import dash_bootstrap_components as dbc
from plot_level import plot_level

#%% Generate water level plot
fig_level, updated = plot_level()

# %% Start Dash app

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[
               {"name": "viewport", "content": "width=device-width, initial-scale=1"},
           ], )
server = app.server

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(f'Last updated on {updated}', href="#")),
        ],
        brand="ENSO 2003 drought monitor",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dbc.Row(
        dcc.Graph(id='fig-level', figure=fig_level, style={'aspect-ratio': '21 / 10'}),
    )
],
    fluid=True)

# %% dunder blip
if __name__ == '__main__':
    app.run(debug=True)

from dash import Dash, html, dcc
import pandas as pd
import plotly.graph_objects as go
import get_telem

###### Get data
#curData = pd.read_pickle('curData.pkl').reset_index()
curData = pd.read_pickle('data/curData.pkl').reset_index()
hisData = pd.read_pickle('data/hisData.pkl').reset_index()

# Calculate statistics
doyMean = hisData.groupby('Doy').Nivel.agg(['mean']).reset_index()
doySD = hisData.groupby('Doy').Nivel.agg(['std']).reset_index() 

# Extract individual series
doy1998 = hisData[hisData['Yr']==1998]
doy2005 = hisData[hisData['Yr']==2005]
doy2010 = hisData[hisData['Yr']==2010]
doy2015 = hisData[hisData['Yr']==2015]
doy2022 = hisData[hisData['Yr']==2022]

# Generate Plot
fig_level = go.Figure([
    # Current data
    go.Scatter(name='2023',x=curData['Doy'],y=curData['Nivel'],mode='lines',line=dict(color='#2c7bb6'),),
    # Historical droughts
    go.Scatter(name='2022',x=doy2022['Doy'],y=doy2022['Nivel'],mode='lines',line=dict(color='#1a9641'),),
    go.Scatter(name='2015',x=doy2015['Doy'],y=doy2015['Nivel'],mode='lines',line=dict(color='#ffffb2'),),
    go.Scatter(name='2010',x=doy2010['Doy'],y=doy2010['Nivel'],mode='lines',line=dict(color='#e31a1c'),),
    go.Scatter(name='2005',x=doy2005['Doy'],y=doy2005['Nivel'],mode='lines',line=dict(color='#fecc5c'),),
    go.Scatter(name='1998',x=doy1998['Doy'],y=doy1998['Nivel'],mode='lines',line=dict(color='#fd8d3c'),),
    # Climatology
    go.Scatter(name='Mean 1979-2022',x=doyMean['Doy'],y=doyMean['mean'],mode='lines',line=dict(color='rgb(0, 0, 0)', dash='dash'),),
    go.Scatter(name='95% CI',x=doySD['Doy'],y=doyMean['mean'] + 1.96 * doySD['std'],mode='lines',marker=dict(color="#444"),
               line=dict(width=0),showlegend=False),
    go.Scatter(name='95% CI',x=doySD['Doy'],y=doyMean['mean'] - 1.96 * doySD['std'],marker=dict(color="#444"),line=dict(width=0),
               mode='lines',fillcolor='rgba(100, 100, 100, 0.2)',fill='tonexty',)
])

fig_level.update_layout(
    yaxis_title='Water level (cm)',
    xaxis_title='Day of the year',    
    #title='Current and historical water leveles, Fonte Boa',
    width=1400,
    height=800,
    margin=dict(l=50,r=50,b=100,t=30,pad=0),
    hovermode='x unified'
)

fig_level.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across")
#fig_level.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
fig_level.update_layout(spikedistance=1000, hoverdistance=100)

# Dash app

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children='ENSO 2003 drought monitor', style={'textAlign':'center'}),
    #dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='fig-level', figure=fig_level)
])

if __name__ == '__main__':
    app.run(debug=True)
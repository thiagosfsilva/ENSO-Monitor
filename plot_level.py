#%%
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import date
pio.renderers.default = "vscode"

TELEM_START_YEAR = 2023  # first year covered by the telemetry (curData) source

#%%
def plot_level():
    #%% Load and merge analog historical + telemetry data
    curData = pd.read_pickle('data/curData.pkl').reset_index()
    hisData = pd.read_pickle('data/hisCota.pkl').reset_index()

    curData['Dt'] = pd.to_datetime(curData['Dt'])
    curData['Yr'] = curData['Dt'].dt.year
    hisData['Dt'] = pd.to_datetime(hisData['Dt'])

    # Convert cm → m in both sources before merging
    curData['Nivel'] = curData['Nivel'] / 100
    hisData['Nivel'] = hisData['Nivel'] / 100

    # hisCota covers the historical baseline; curData covers TELEM_START_YEAR onward
    allData = pd.concat([
        hisData[hisData['Yr'] < TELEM_START_YEAR][['Dt', 'Doy', 'Nivel', 'Yr']],
        curData[curData['Yr'] >= TELEM_START_YEAR][['Dt', 'Doy', 'Nivel', 'Yr']]
    ]).sort_values('Dt').reset_index(drop=True)

    #%% Calculate climatology statistics from the analog baseline only
    baseline = hisData[hisData['Yr'] < TELEM_START_YEAR]
    doyMean = baseline.groupby('Doy').Nivel.agg(['mean']).reset_index()
    doySD   = baseline.groupby('Doy').Nivel.agg(['std']).reset_index()

    #%% X-axis: current year's dates (365 values) used as the DOY template
    current_year = date.today().year
    x_axis = allData[allData['Yr'] == current_year]['Dt'].values

    #%% Extract individual series (365 rows each, DOY order)
    doy1998 = allData[allData['Yr'] == 1998]['Nivel'].values
    doy2005 = allData[allData['Yr'] == 2005]['Nivel'].values
    doy2010 = allData[allData['Yr'] == 2010]['Nivel'].values
    #doy2015 = allData[allData['Yr'] == 2015]['Nivel'].values
    doy2022 = allData[allData['Yr'] == 2022]['Nivel'].values
    doy2023 = allData[allData['Yr'] == 2023]['Nivel'].values
    doy2024 = allData[allData['Yr'] == 2024]['Nivel'].values
    doy2025 = allData[allData['Yr'] == 2025]['Nivel'].values
    doy_cur = allData[allData['Yr'] == current_year]['Nivel'].values

    #%% Generate Plot
    fig_level = go.Figure([
        # Historical droughts
        go.Scatter(name='1998',x=x_axis,y=doy1998,mode='lines',line=dict(color='#e31a1c',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2005',x=x_axis,y=doy2005,mode='lines',line=dict(color='#fd8d3c',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2010',x=x_axis,y=doy2010,mode='lines',line=dict(color='#800026',width=1, smoothing=0.1),line_shape='spline'),
        #go.Scatter(name='2015',x=x_axis,y=doy2015,mode='lines',line=dict(color='#fecc5c',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2022',x=x_axis,y=doy2022,mode='lines',line=dict(color='#1a9641',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2023',x=x_axis,y=doy2023,mode='lines',line=dict(color='#2c7bb6', width=1, smoothing=1),line_shape='spline'),
        go.Scatter(name='2024',x=x_axis,y=doy2024,mode='lines',line=dict(color='#FF0000', width=2, smoothing=1),line_shape='spline'),
        go.Scatter(name='2025',x=x_axis,y=doy2025,mode='lines',line=dict(color='#fecc5c', width=2, smoothing=1),line_shape='spline'),
        # Current year
        go.Scatter(name=str(current_year),x=x_axis,y=doy_cur,mode='lines',line=dict(color='#FF0000', width=4, smoothing=1),line_shape='spline'),
        # Climatology
        go.Scatter(name='Mean/Média 1979-2022',x=x_axis,y=doyMean['mean'],mode='lines',line=dict(color='rgb(100, 100, 100)', dash='dash'),line_shape='spline'),
        go.Scatter(name='95% CI / IC', x=x_axis,y=doyMean['mean'] + 1.96 * doySD['std'],mode='lines',marker=dict(color="#444"),
                line=dict(width=0, smoothing=0.5),showlegend=False,line_shape='spline'),
        go.Scatter(name='95% CI / IC',x=x_axis,y=doyMean['mean'] - 1.96 * doySD['std'],marker=dict(color="#444"),line=dict(width=0, smoothing=0.5),
                mode='lines',fillcolor='rgba(100, 100, 100, 0.2)',fill='tonexty',line_shape='spline')
    ])

    fig_level.update_layout(
        yaxis_title="Water level / Nivel d'Agua (m)",
        xaxis_title='Day of the year / Dia do Ano',
        margin=dict(l=50,r=50,b=100,t=30,pad=0),
        hovermode='x unified',
    )

    x_start = f'{current_year}-01-01'
    x_end   = f'{current_year}-12-31'
    fig_level.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", range=[x_start, x_end])
    fig_level.update_layout(spikedistance=1000, hoverdistance=100)

    #%%
    return fig_level

#%%
if __name__ == "__main__":
    #%%
    figure = plot_level()
    figw = go.FigureWidget(figure)
    figw.show()

# %%


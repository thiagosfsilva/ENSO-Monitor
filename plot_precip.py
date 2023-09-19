#%%
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "vscode"
from numpy import nanstd
from numpy import nanmean

#%%
def plot_level():
    #%% Get water level data
    curData = pd.read_pickle('data/curData.pkl').reset_index()
    hisData = pd.read_pickle('data/hisPrec.pkl').reset_index()
    #curData.head()

    #%% Convert data to datetime format
    curData['Date'] = pd.to_datetime(curData['Date'], format='%Y-%m-%d')
    hisData['Doy'] = pd.to_numeric(hisData['dt'].dt.dayofyear,downcast='float')

    #%% Calculate statistics
    doyMean = hisData.groupby('Doy').agg({'value': [ nanmean, nanstd ]}).reset_index() 



    #%% Generate Plot
    fig_level = go.Figure([
        # Current data
        go.Scatter(name='2023', x=curData['Date'].dt.dayofyear, y=curData['Nivel'], mode='lines',
                   line=dict(color='#2c7bb6', width=4, smoothing=1),),
        # Historical droughts
        go.Scatter(name='2022', x=doy2022['Doy'], y=doy2022['Nivel'], mode='lines',
                   line=dict(color='#1a9641', width=1, smoothing=0.1),),
        go.Scatter(name='2015', x=doy2015['Doy'], y=doy2015['Nivel'], mode='lines',
                   line=dict(color='#fecc5c', width=1, smoothing=0.1),),
        go.Scatter(name='2010', x=doy2010['Doy'], y=doy2010['Nivel'], mode='lines',
                   line=dict(color='#800026', width=1, smoothing=0.1),),
        go.Scatter(name='2005', x=doy2005['Doy'], y=doy2005['Nivel'], mode='lines',
                   line=dict(color='#fd8d3c', width=1, smoothing=0.1),),
        go.Scatter(name='1998', x=doy1998['Doy'], y=doy1998['Nivel'], mode='lines',
                   line=dict(color='#e31a1c', width=1, smoothing=0.1),),
        # Climatology
        go.Scatter(name='Mean 1979-2022', x=doyMean['Doy'], y=doyMean['mean'], mode='lines',
                   line=dict(color='rgb(100, 100, 100)', dash='dash'), line_shape='spline'),
        go.Scatter(name='95% CI', x=doySD['Doy'], y=doyMean['mean'] + 1.96 * doySD['std'], mode='lines',
                   marker=dict(color="#444"),
                   line=dict(width=0, smoothing=0.5), showlegend=False, line_shape='spline'),
        go.Scatter(name='95% CI', x=doySD['Doy'], y=doyMean['mean'] - 1.96 * doySD['std'], marker=dict(color="#444"),
                   line=dict(width=0, smoothing=0.5),
                   mode='lines', fillcolor='rgba(100, 100, 100, 0.2)', fill='tonexty', line_shape='spline')
    ])

    fig_level.update_layout(
        yaxis_title='Water level (meters)',
        xaxis_title='Day of the year',
        # title='Current and historical water levels, Fonte Boa',
        # width=1400,
        # height=800,
        margin=dict(l=50, r=50, b=100, t=30, pad=0),
        hovermode='x unified',
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
    )

    fig_level.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across")
    # fig_level.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
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

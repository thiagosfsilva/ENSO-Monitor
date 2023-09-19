#%%
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "vscode"
from numpy import nanstd
#%%
def plot_precip():
    #%Get water level data
    curData = pd.read_pickle('data/curData.pkl').reset_index()
    hisData = pd.read_pickle('data/hisPrec.pkl').reset_index()
    #curData.head()

    # Convert data to datetime format
    curData['Dt'] = pd.to_datetime(curData['Dt'], format='%Y-%m-%d')

    # Calculate statistics
    doyMean = hisData.groupby('Doy').Chuva.agg(['mean']).reset_index()
    doySD = hisData.groupby('Doy').Chuva.agg([nanstd]).reset_index()

    #Generate Plot
    fig_level = go.Figure([
        # Current data
        go.Bar(name=' Rainfall/Chuva 2023', x=curData['Dt'], y=curData['Chuva'],),# hovertemplate = '<br>Date/Data: %{x}</br>' + '<br><b>Rainfall/Chuva</b>: %{y}<br>', showlegend = False),
        #            line=dict(color='#2c7bb6', width=4, smoothing=1),),
        # Historical droughts
        #go.Scatter(name='2022', x=doy2022['Doy'], y=doy2022['Nivel'], mode='lines',
        #           line=dict(color='#1a9641', width=1, smoothing=0.1),),
        #go.Scatter(name='2015', x=doy2015['Doy'], y=doy2015['Nivel'], mode='lines',
        #           line=dict(color='#fecc5c', width=1, smoothing=0.1),),
        #go.Scatter(name='2010', x=doy2010['Doy'], y=doy2010['Nivel'], mode='lines',
        #           line=dict(color='#800026', width=1, smoothing=0.1),),
        #go.Scatter(name='2005', x=doy2005['Doy'], y=doy2005['Nivel'], mode='lines',
        #           line=dict(color='#fd8d3c', width=1, smoothing=0.1),),
        #go.Scatter(name='1998', x=doy1998['Doy'], y=doy1998['Nivel'], mode='lines',
        #           line=dict(color='#e31a1c', width=1, smoothing=0.1),),
        ## Climatology
        go.Bar(name='Nonzero Mean / Media - dias com chuva', x=curData['Dt'], y=doyMean['mean'],)# hovertemplate = '<br><b>Mean/Média</b>: %{y}<br>', showlegend = False),
        #           line=dict(color='rgb(100, 100, 100)', dash='dash'), line_shape='spline'),
        #go.Scatter(name='95% CI', x=doySD['Doy'], y=doyMean['mean'] + 1.96 * doySD['std'], mode='lines',
        #           marker=dict(color="#444"),
        #           line=dict(width=0, smoothing=0.5), showlegend=False, line_shape='spline'),
        #go.Scatter(name='95% CI', x=doySD['Doy'], y=doyMean['mean'] - 1.96 * doySD['std'], marker=dict(color="#444"),
        #           line=dict(width=0, smoothing=0.5),
        #           mode='lines', fillcolor='rgba(100, 100, 100, 0.2)', fill='tonexty', line_shape='spline')
    ])

    fig_level.update_layout(
        yaxis_title='Rainfall / Chuva (mm)',
        xaxis_title='',
        # title='Current and historical water levels, Fonte Boa',
        # width=1400,
        # height=800,
        margin=dict(l=50, r=50, b=100, t=30, pad=0),
        hovermode='x unified',
    )

    fig_level.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across",range=['2023-01-01', '2023-12-31'])
    fig_level.update_layout(spikedistance=1000, hoverdistance=100)

    #
    return fig_level

#%%
if __name__ == "__main__":
    #%%
    figure = plot_precip()
    figw = go.FigureWidget(figure)
    figw.show()

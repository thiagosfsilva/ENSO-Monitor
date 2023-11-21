#%%
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
pio.renderers.default = "browser"

#%%
def plot_level():
    #%% Get water level data
    curData = pd.read_pickle('data/curData.pkl').reset_index()
    hisData = pd.read_pickle('data/hisCota.pkl').reset_index()
    #curData.head()

    #%% Convert to meters
    curData.Nivel = curData.Nivel / 100
    hisData.Nivel = hisData.Nivel / 100

    #%% Convert data to datetime format
    curData['Dt'] = pd.to_datetime(curData['Dt'], format='%Y-%m-%d')

    #%% Calculate statistics
    doyMean = hisData.groupby('Doy').Nivel.agg(['mean']).reset_index()
    doySD = hisData.groupby('Doy').Nivel.agg(['std']).reset_index()
    

    #%% TEST
    doySD.plot()


    #%% Extract individual series
    doy1998 = hisData[hisData['Yr']==1998]
    doy2005 = hisData[hisData['Yr']==2005]
    doy2010 = hisData[hisData['Yr']==2010]
    #doy2015 = hisData[hisData['Yr']==2015]
    doy2022 = hisData[hisData['Yr']==2022]

    #%% Generate Plot
    fig_level = go.Figure([
        # Current data
        #go.Scatter(name='2023',x=curData['Dt'],y=curData['Nivel'],mode='lines',line=dict(color='#2c7bb6', width=4, smoothing=1),line_shape='spline'),
        # Historical droughts
        #go.Scatter(name='2022',x=curData['Dt'],y=doy2022['Nivel'],mode='lines',line=dict(color='#1a9641',width=1, smoothing=0.1),line_shape='spline'),
        #go.Scatter(name='2015',x=curData['Dt'],y=doy2015['Nivel'],mode='lines',line=dict(color='#fecc5c',width=1, smoothing=0.1),line_shape='spline'),
        #go.Scatter(name='2010',x=curData['Dt'],y=doy2010['Nivel'],mode='lines',line=dict(color='#800026',width=1, smoothing=0.1),line_shape='spline'),
        #go.Scatter(name='2005',x=curData['Dt'],y=doy2005['Nivel'],mode='lines',line=dict(color='#fd8d3c',width=1, smoothing=0.1),line_shape='spline'),
        #go.Scatter(name='1998',x=curData['Dt'],y=doy1998['Nivel'],mode='lines',line=dict(color='#e31a1c',width=1, smoothing=0.1),line_shape='spline'),
        # Climatology
        go.Scatter(name='Mean/Média 1979-2022',x=curData['Dt'],y=doyMean['mean'],mode='lines',line=dict(color='rgb(100, 100, 100)', dash='dash'),line_shape='spline'),
        #go.Scatter(name='95% CI / IC', x=curData['Dt'],y=doyMean['mean'] + 1.96 * doySD['std'],mode='lines',marker=dict(color="#444"),
        #        line=dict(width=0, smoothing=0.5),showlegend=False,line_shape='spline'),
        #go.Scatter(name='95% CI / IC',x=curData['Dt'],y=doyMean['mean'] - 1.96 * doySD['std'],marker=dict(color="#444"),line=dict(width=0, smoothing=0.5),
        #        mode='lines',fillcolor='rgba(100, 100, 100, 0.2)',fill='tonexty',line_shape='spline')
    ])
    #%%
    fig_level.update_layout(
        yaxis_title="Water level / Nivel d'Agua (m)",
        xaxis_title='Day of the year / Dia do Ano',    
        #title='Current and historical water leveles, Fonte Boa',
        #width=1400,
        #height=800,
        margin=dict(l=50,r=50,b=100,t=30,pad=0),
        hovermode='x unified',
        #xaxis=dict(
        #    tickmode='array',
        #    tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
        #    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        #),
    )

    fig_level.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across",range=['2023-01-01', '2023-12-31'])
    fig_level.update_layout(spikedistance=1000, hoverdistance=100)
    
    fig_level.show()

    #%%
    return fig_level

#%%
if __name__ == "__main__":
    #%%
    figure = plot_level()
    figw = go.FigureWidget(figure)
    figw.show()


#%%
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"


#%%
def plot_level():
    #%% Get water level data
    curData = pd.read_parquet('data/currentData.parquet').reset_index()
    hisData = pd.read_parquet('data/historicalLevels_12351000.parquet').reset_index()
    hisData['doy'] = hisData['doy'].astype('int32')
    print(curData.head())
    print(hisData.head())

    #%% Convert to meters
    curData.level = curData.level / 100
    hisData.level = hisData.level / 100
    print(curData.head())
    print(hisData.head())
    #%% Convert data to datetime format
    curData['dt'] = pd.to_datetime(curData['dt'], format='%Y-%m-%d')

    #%% Calculate statistics
    doyMean = hisData.groupby('doy').agg(level =('level', 'mean')).reset_index()
    doySD = hisData.groupby('doy').agg(level =('level', 'std')).reset_index()
    
    #%% Extract individual series
    doy1998 = hisData[hisData['yr']==1998]
    doy2005 = hisData[hisData['yr']==2005]
    doy2010 = hisData[hisData['yr']==2010]
    doy2015 = hisData[hisData['yr']==2015]
    doy2022 = hisData[hisData['yr']==2022]

    #%% Test series
    fig, ax = plt.subplots()
    ax.plot(doy2015.doy, doy2015.level)
    plt.show()

    #%% "Clone' 2023 dates to other datasets to enable plotting
    doyMean['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doySD['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doy1998['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doy2005['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doy2010['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doy2015['dt'] = pd.date_range('2023-01-01','2023-12-31')
    doy2022['dt'] = pd.date_range('2023-01-01','2023-12-31')

    #%% Generate Plot
    fig_level = go.Figure([
        # Current data
        go.Scatter(name='2023',x=curData['dt'],y=curData['level'],mode='lines',line=dict(color='#2c7bb6', width=4, smoothing=1),line_shape='spline'),
        # Historical droughts
        go.Scatter(name='2015',x=doy2015['dt'],y=doy2015['level'],mode='lines',line=dict(color='#fecc5c',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2022',x=doy2022['dt'],y=doy2022['level'],mode='lines',line=dict(color='#1a9641',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2010',x=doy2010['dt'],y=doy2010['level'],mode='lines',line=dict(color='#800026',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='2005',x=doy2005['dt'],y=doy2005['level'],mode='lines',line=dict(color='#fd8d3c',width=1, smoothing=0.1),line_shape='spline'),
        go.Scatter(name='1998',x=doy1998['dt'],y=doy1998['level'],mode='lines',line=dict(color='#e31a1c',width=1, smoothing=0.1),line_shape='spline'),
        # Climatology
        go.Scatter(name='Mean/Média 1979-2022',x=doyMean['dt'],y=doyMean['level'],mode='lines',line=dict(color='rgb(100, 100, 100)', dash='dash'),line_shape='spline'),
        go.Scatter(name='95% CI / IC', x=doyMean['dt'],y=doyMean['level'] + 1.96 * doySD['level'],mode='lines',marker=dict(color="#444"),
                line=dict(width=0, smoothing=0.5),showlegend=False,line_shape='spline'),
        go.Scatter(name='95% CI / IC',x=doyMean['dt'],y=doyMean['level'] - 1.96 * doySD['level'],marker=dict(color="#444"),line=dict(width=0, smoothing=0.5),
                mode='lines',fillcolor='rgba(100, 100, 100, 0.2)',fill='tonexty',line_shape='spline')
    ])
    #%%
    fig_level.update_layout(
        yaxis_title="Water level / Nível (m)",
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
    
    #%%
    return fig_level

#%%
if __name__ == "__main__":
    #%%
    figure = plot_level()
    figw = go.FigureWidget(figure)
    figw.show()



#%%
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import date
pio.renderers.default = "vscode"

STATIONS = {
    '12351000': {'name': 'Fonte Boa',             'telem_start': 2023},
    '11400000': {'name': 'S. P. de Olivenca',     'telem_start': 2026},
    '14990000': {'name': 'Manaus',                'telem_start': 2022},
    '17050001': {'name': 'Obidos',                'telem_start': 2026},
}

DROUGHT_YEARS = [1998, 2005, 2010, 2022, 2023, 2024, 2025]

DROUGHT_STYLE = {
    1998: {'color': '#e31a1c', 'width': 1},
    2005: {'color': '#fd8d3c', 'width': 1},
    2010: {'color': '#800026', 'width': 1},
    2022: {'color': '#1a9641', 'width': 1},
    2023: {'color': '#2c7bb6', 'width': 1},
    2024: {'color': '#FF0000', 'width': 2},
    2025: {'color': '#fecc5c', 'width': 2},
}


def plot_station(station_code):
    cfg = STATIONS[station_code]
    telem_start = cfg['telem_start']

    hisData = pd.read_pickle(f'data/levels/hisCota_{station_code}.pkl').reset_index()
    hisData['Dt'] = pd.to_datetime(hisData['Dt'])
    hisData['Yr'] = hisData['Dt'].dt.year
    hisData['Nivel'] = hisData['Nivel'] / 100

    try:
        curData = pd.read_pickle(f'data/levels/curData_{station_code}.pkl').reset_index()
        curData['Dt'] = pd.to_datetime(curData['Dt'])
        curData['Yr'] = curData['Dt'].dt.year
        curData['Nivel'] = curData['Nivel'] / 100
        has_telem = True
    except FileNotFoundError:
        has_telem = False

    parts = [hisData[hisData['Yr'] < telem_start][['Dt', 'Doy', 'Nivel', 'Yr']]]
    if has_telem:
        parts.append(curData[curData['Yr'] >= telem_start][['Dt', 'Doy', 'Nivel', 'Yr']])
    allData = pd.concat(parts).sort_values('Dt').reset_index(drop=True)

    # Climatology from analog baseline only
    baseline = hisData[hisData['Yr'] < telem_start]
    clim_label = f"{baseline['Yr'].min()}-{baseline['Yr'].max()}"
    doyMean = baseline.groupby('Doy')['Nivel'].mean()
    doySD   = baseline.groupby('Doy')['Nivel'].std()

    current_year = date.today().year
    x_axis = allData[allData['Yr'] == current_year]['Dt'].values

    traces = []

    # Historical drought years — skip silently if fewer than 300 data points
    for yr in DROUGHT_YEARS:
        s = DROUGHT_STYLE[yr]
        yr_data = allData[allData['Yr'] == yr]['Nivel'].values
        if len(yr_data) < 300:
            continue
        traces.append(go.Scatter(
            name=str(yr), x=x_axis, y=yr_data, mode='lines',
            line=dict(color=s['color'], width=s['width'], smoothing=1),
            line_shape='spline'
        ))

    # Current year — always shown even when partial
    cur_data = allData[allData['Yr'] == current_year]['Nivel'].values
    traces.append(go.Scatter(
        name=str(current_year), x=x_axis, y=cur_data, mode='lines',
        line=dict(color='#FF0000', width=4, smoothing=1),
        line_shape='spline'
    ))

    # Climatology mean + 95% CI band
    traces += [
        go.Scatter(
            name=f'Media {clim_label}', x=x_axis, y=doyMean.values,
            mode='lines', line=dict(color='rgb(100,100,100)', dash='dash'),
            line_shape='spline'
        ),
        go.Scatter(
            name='95% CI', x=x_axis, y=(doyMean + 1.96 * doySD).values,
            mode='lines', marker=dict(color='#444'), line=dict(width=0, smoothing=0.5),
            showlegend=False, line_shape='spline'
        ),
        go.Scatter(
            name='95% CI', x=x_axis, y=(doyMean - 1.96 * doySD).values,
            mode='lines', marker=dict(color='#444'), line=dict(width=0, smoothing=0.5),
            fill='tonexty', fillcolor='rgba(100,100,100,0.2)', line_shape='spline'
        ),
    ]

    fig = go.Figure(traces)
    fig.update_layout(
        title=dict(text=cfg['name'], x=0.5, font=dict(size=14)),
        yaxis_title="Nivel d'Agua (m)",
        xaxis_title='Dia do Ano',
        margin=dict(l=50, r=20, b=80, t=50, pad=0),
        hovermode='x unified',
        legend=dict(font=dict(size=10)),
    )
    x_start = f'{current_year}-01-01'
    x_end   = f'{current_year}-12-31'
    fig.update_xaxes(showspikes=True, spikecolor='green', spikesnap='cursor',
                     spikemode='across', range=[x_start, x_end])
    fig.update_layout(spikedistance=1000, hoverdistance=100)
    return fig


def plot_level():
    return {code: plot_station(code) for code in STATIONS}


#%%
if __name__ == '__main__':
    import plotly.io as pio
    pio.renderers.default = 'browser'
    figs = plot_level()
    for fig in figs.values():
        fig.show()

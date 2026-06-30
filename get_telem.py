#%% imports
import io
import requests
import pandas as pd
from datetime import date, datetime

td = date.today().strftime("%Y-%m-%d")

# dataInicio per station: year from which we rely on telemetry
# (analog coverage determines the cutoff — see plot_level.py STATIONS config)
STATION_CONFIGS = {
    '12351000': '2023-01-01',  # Fonte Boa       — analog ends ~2022
    '11400000': '2026-01-01',  # S.P. Olivenca   — analog covers to 2025
    '14990000': '2022-01-01',  # Manaus          — analog ends 2014; need 2022+ drought years
    '17050001': '2026-01-01',  # Obidos          — analog covers to 2025
}

ANA_URL = 'http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos'


def get_telem(station_code, data_inicio, td, export=False):
    params = {'codEstacao': station_code, 'dataInicio': data_inicio, 'dataFim': td}

    print(f'Fetching {station_code} ({data_inicio} to {td})...')
    response = requests.get(ANA_URL, params=params)

    rawTable = pd.read_xml(io.BytesIO(response.content),
                           namespaces={'msdata': 'urn:schemas-microsoft-com:xml-msdata'},
                           xpath='.//DadosHidrometereologicos')
    rawTable['DataHora'] = pd.to_datetime(rawTable['DataHora'])
    rawTable['Doy'] = rawTable['DataHora'].dt.dayofyear
    rawTable['Dt'] = rawTable['DataHora'].dt.date

    curData = rawTable.groupby(['Dt', 'Doy']).agg({'Vazao': 'max', 'Nivel': 'max', 'Chuva': 'sum'})

    # Pad with NaN rows to end of current year
    lastdate, lastdoy = curData.index[-1]
    emptyDate = pd.date_range(lastdate, periods=365 - lastdoy + 1).date.tolist()
    emptyDoy  = range(lastdoy, 365)
    emptyVals = [None] * len(emptyDate)
    emptyDF = pd.DataFrame(
        list(zip(emptyDate, emptyDoy, emptyVals, emptyVals, emptyVals)),
        columns=['Dt', 'Doy', 'Vazao', 'Nivel', 'Chuva']
    )
    emptyDF.set_index(['Dt', 'Doy'], inplace=True)
    curData = pd.concat([curData, emptyDF])

    if export:
        curData.to_csv(f'data/levels/curData_{station_code}.csv')
        curData.to_pickle(f'data/levels/curData_{station_code}.pkl')
        print(f'  Saved curData_{station_code}')

    return curData


if __name__ == '__main__':
    for station_code, data_inicio in STATION_CONFIGS.items():
        get_telem(station_code, data_inicio, td=td, export=True)

    upDate = pd.DataFrame({'updated': [datetime.today().date()]})
    upDate.to_pickle('data/levels/upDate.pkl')
    print(f'Done. Updated at {datetime.today()}')

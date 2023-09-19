import requests
import pandas as pd
from datetime import datetime


def get_telem(export=False):
    # Set request parameters
    ana_url = 'http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos'

    params = {'codEstacao': '12351000',
              'dataInicio': '2023-01-01',
              'dataFim': '2023-12-01'}

    # Make request
    response = requests.get(ana_url, params=params)
    upDate = pd.DataFrame([datetime.today().date()])

    # Parse response as dataframe and clean it
    rawTable = pd.read_xml(response.content, namespaces={'msdata': "urn:schemas-microsoft-com:xml-msdata"},
                           xpath='.//DadosHidrometereologicos')
    rawTable.dropna()
    rawTable['DataHora'] = pd.to_datetime(rawTable['DataHora'])
    rawTable['Doy'] = rawTable['DataHora'].dt.dayofyear
    rawTable['Dt'] = pd.to_datetime(rawTable['DataHora']).dt.date
    rawTable['Time'] = pd.to_datetime(rawTable['DataHora']).dt.time
    rawTable.head()

    # Aggregate hydro data
    curData = rawTable.groupby(['Dt', 'Doy']).agg({
        'Vazao': 'max',
        'Nivel': 'max',
        'Chuva': 'sum'})

    curData.head()

    # Export to file
    if export:
        curData.to_pickle('data/curData.pkl')
        upDate.to_pickle('data/upDate.pkl')
        print(f'Data updated on {datetime.today()}')

    return curData


if __name__ == "__main__":
    get_telem(export=True)

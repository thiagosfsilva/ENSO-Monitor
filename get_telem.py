#%% imports
import requests
import pandas as pd
from datetime import date,datetime

#%% 
td = date.today().strftime("%Y-%m-%d")

#%%
def get_telem(td, export=False):
    #%% Set request parameters
    ana_url = 'http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos'

    params = {'codEstacao': '12351000',
              'dataInicio': '2023-01-01',
              'dataFim': td}

    #%% Make request
    print('Making request...')
    response = requests.get(ana_url, params=params)
    upDate = pd.DataFrame({'updated':[datetime.today().date()]})['updated'].values[0]

    #%% Parse response as dataframe and clean it
    ('Parsing...')
    rawTable = pd.read_xml(response.content, namespaces={'msdata': "urn:schemas-microsoft-com:xml-msdata"},
                           xpath='.//DadosHidrometereologicos')
    rawTable.dropna()
    rawTable['DataHora'] = pd.to_datetime(rawTable['DataHora'])
    rawTable['Doy'] = rawTable['DataHora'].dt.dayofyear
    rawTable['Dt'] = pd.to_datetime(rawTable['DataHora']).dt.date
    rawTable['Time'] = pd.to_datetime(rawTable['DataHora']).dt.time
    rawTable.head()

    #%% Aggregate hydro data
    curData = rawTable.groupby(['Dt', 'Doy']).agg({
        'Vazao': 'max',
        'Nivel': 'max',
        'Chuva': 'sum'})

    curData.head()

    #%% Pad with empty values until the end of the year
    lastdate, lastdoy = curData.index[-1]
    emptyDate = pd.date_range(lastdate, periods=365-lastdoy+1).date.tolist()
    print(emptyDate)
    emptyDoy = range(lastdoy,365)
    emptyVals = [None] * len(emptyDate)
    emptyDF = pd.DataFrame(list(zip(emptyDate, emptyDoy,emptyVals,emptyVals,emptyVals)), columns =['Dt', 'Doy','Vazao','Nivel','Chuva']) 
    emptyDF.set_index(['Dt','Doy'], drop=True, append=False, inplace=True, verify_integrity=True)
    curData = pd.concat([curData,emptyDF])
    print(curData) 


    #%%Export to file
    if export:
        #%%
        curData.to_csv('data/curData.csv')
        curData.to_pickle('data/curData.pkl')
        #upDate.to_pickle('data/upDate.pkl')
        print(f'Data updated on {datetime.today()}')
    #%%
    return curData


if __name__ == "__main__":
    get_telem(td=td,export=True)

# %%

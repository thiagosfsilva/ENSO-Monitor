#%% imports
import requests
from io import StringIO
import pandas as pd
from datetime import datetime

#%%
def get_telem_github(code = 12351000,export=False):
    #%% Set request parameters
    code=12351000
    ana_url = f'https://github.com/anagovbr/dados-estacoes-hidro/raw/main/dados/{code}.csv'
    
    #%% Make request
    response = requests.get(ana_url).content
    rawTable = pd.read_csv(StringIO(response.decode('utf-8')),delimiter=';',
                           header=0,
                           names = ['DataHora',	'Nivel_Sensor',	'Nivel_Display(cm)',
                                    'Chuva(mm)', 'Chuva_Acum', 'Temp_H2O','	Press_Atm(mb)',
                                    'Temp_Int(C)',	'Bateria(V)','	OffSet(cm)'])
    upDate = datetime.today().date()
    print(upDate)

    #%% Parse response as dataframe and clean it
    rawTable['DataHora'] = pd.to_datetime(rawTable['DataHora'],format='%d/%m/%Y %H:%M:%S')
    rawTable['doy'] = rawTable['DataHora'].dt.dayofyear
    rawTable['dt'] = pd.to_datetime(rawTable['DataHora']).dt.date
    rawTable['Time'] = pd.to_datetime(rawTable['DataHora']).dt.time
    rawTable.head()

    #%% Aggregate hydro data
    curDataNew = rawTable.groupby(['dt', 'doy']).agg(
        level = ('Nivel_Sensor', 'max'),
        precip = ('Chuva_Acum', 'max'),
        )

    curDataNew.head()

    #%% Pad with empty values until the end of the year
    lastdate, lastdoy = curDataNew.index[-1]
    emptyDate = pd.date_range(lastdate, periods=365-lastdoy+1).date.tolist()
    emptyDoy = range(lastdoy,365)
    emptyVals = [None] * len(emptyDate)
    emptyDF = pd.DataFrame(list(zip(emptyDate, emptyDoy,emptyVals,emptyVals)),
                           columns =['dt', 'doy','level','precip'])
    emptyDF.set_index(['dt','doy'], drop=False, append=False, inplace=True, verify_integrity=True)
    curData = pd.concat([curDataNew,emptyDF])
    print(curDataNew)

    #%% merge with old data 
    curDataOld = pd.read_parquet('data/currentData_prehack.parquet')
    firstdate, firstdoy = curDataNew.index[0]
    curDataOld = curDataOld[curDataOld['doy'] < firstdoy]
    curDataOld.set_index(['dt','doy'], drop=True, append=False, inplace=True, verify_integrity=True)
    curData = pd.concat([curDataOld,curDataNew])
    print(curData.head())
    print(curData.tail())


    #%%Export to file
    if export:
        #%%
        #curData.to_pickle('data/curData.pkl')
        curData.to_parquet('data/currentData.parquet')
        with open('upDate.txt', 'w') as f:
            f.write(str(upDate))
        print(f'Data updated on {datetime.today()}')
    #%%
    return curData


if __name__ == "__main__":
    get_telem_github(export=True)

# %%

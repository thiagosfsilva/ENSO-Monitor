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
    rawTable['Doy'] = rawTable['DataHora'].dt.dayofyear
    rawTable['Dt'] = pd.to_datetime(rawTable['DataHora']).dt.date
    rawTable['Time'] = pd.to_datetime(rawTable['DataHora']).dt.time
    rawTable.head()

    #%% Aggregate hydro data
    curData = rawTable.groupby(['Dt', 'Doy']).agg(
        Nivel = ('Nivel_Sensor', 'max'),
        Chuva = ('Chuva_Acum', 'max'),
        )

    curData.head()

    #%% Pad with empty values until the end of the year
    lastdate, lastdoy = curData.index[-1]
    emptyDate = pd.date_range(lastdate, periods=365-lastdoy+1).date.tolist()
    emptyDoy = range(lastdoy,365)
    emptyVals = [None] * len(emptyDate)
    emptyDF = pd.DataFrame(list(zip(emptyDate, emptyDoy,emptyVals,emptyVals)),
                           columns =['Dt', 'Doy','Nivel','Chuva']) 
    emptyDF.set_index(['Dt','Doy'], drop=True, append=False, inplace=True, verify_integrity=True)
    curData = pd.concat([curData,emptyDF])
    print(curData) 

    #%% merge with old data 
    curDataOld = pd.read_pickle('data/curDataOld.pkl')
    curData = pd.concat([curDataOld,curData])
    print(curData.head())
    print(curData.tail())
    

    #%%Export to file
    if export:
        #%%
        curData.to_pickle('data/curData.pkl')
        with open('upDate.txt', 'w') as f:
            f.write(str(upDate))
        print(f'Data updated on {datetime.today()}')
    #%%
    return curData


if __name__ == "__main__":
    get_telem_github(export=True)

# %%

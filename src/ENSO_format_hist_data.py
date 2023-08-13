import pandas as pd

# Historical Data (static)
levData = pd.read_csv('data/cotas_C_12351000_daily.csv').rename(columns={'dt':'Dt','precip':'Nivel'})
levData['Dt'] = pd.to_datetime(levData['Dt'])
levData['Doy'] = levData['Dt'].dt.dayofyear
levData['Yr'] = pd.to_datetime(levData['Dt']).dt.year
levData = levData[levData['Yr']<2023]
print(levData.tail())
lev

levData.to_pickle('../data/hisData.pkl')

precData = pd.read_csv('..data/cotas_C_12351000_daily.csv').rename(columns={'dt':'Date','precip':'Nivel'})
precData['Dt'] = pd.to_datetime(precData['Date'])
precData['Doy'] = precData['Dt'].dt.dayofyear
precData['Yr'] = pd.to_datetime(precData['Date']).dt.year
precData = precData[precData['Yr']<2023]
print(precData.head())

precData.to_pickle('../data/hisPrecData.pkl')
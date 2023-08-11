import pandas as pd

# Historical Data (static)
hisData = pd.read_csv('Water_level/fonte_boa_12351000/cotas_C_12351000_daily.csv').rename(columns={'dt':'Dt','precip':'Nivel'})
hisData['Dt'] = pd.to_datetime(hisData['Dt'])
hisData['Doy'] = hisData['Dt'].dt.dayofyear
hisData['Yr'] = pd.to_datetime(hisData['Dt']).dt.year
hisData = hisData[hisData['Yr']<2023]
print(hisData.head())

hisData.to_pickle('hisData.pkl')
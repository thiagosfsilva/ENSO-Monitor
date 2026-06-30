#%%
import zipfile
import pandas as pd
import glob
import os

#%% Config — run from project root
RAW_DIR = 'data/levels/raw'
OUT_DIR = 'data/levels'

#%% Helper: find zip for a given station code
def find_zip(station_code):
    matches = glob.glob(os.path.join(RAW_DIR, f'cotasEstacao_{station_code}_*.zip'))
    if not matches:
        raise FileNotFoundError(f'No zip found for station {station_code} in {RAW_DIR}')
    return matches[0]

#%% Core processing function
def process_station(station_code):
    zip_path = find_zip(station_code)
    print(f'{station_code}: reading {os.path.basename(zip_path)}')

    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(f'{station_code}_Cotas.csv') as f:
            raw = pd.read_csv(f, skiprows=14, sep=';', decimal=',', encoding='latin-1')

    # Keep only daily averages
    raw = raw[raw['MediaDiaria'] == 1].copy()
    raw['Data'] = pd.to_datetime(raw['Data'], format='%d/%m/%Y')

    # For months with both consistency levels, prefer NivelConsistencia=2 (checked)
    raw = raw.sort_values(['Data', 'NivelConsistencia'], ascending=[True, False])
    raw = raw.drop_duplicates(subset='Data', keep='first')

    # Pivot Cota01–Cota31 (columns 16:47) into daily rows
    n_rows = len(raw)
    stacked = []
    for r in range(n_rows):
        row = raw.iloc[r]
        year = row['Data'].strftime('%Y')
        month = row['Data'].strftime('%m')
        d_vals = raw.iloc[r, 16:47].values
        for day in range(1, 32):
            stacked.append({
                'Dt': f'{year}-{month}-{day:02d}',
                'Nivel': d_vals[day - 1]
            })

    df = pd.DataFrame(stacked)
    df['Dt'] = pd.to_datetime(df['Dt'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['Dt', 'Nivel'])
    df['Nivel'] = df['Nivel'].astype(float)

    # Drop Feb 29 so every year is exactly 365 rows
    df = df[~((df['Dt'].dt.day == 29) & (df['Dt'].dt.month == 2))]

    df['Dy']  = df['Dt'].dt.day.astype('int32')
    df['Mn']  = df['Dt'].dt.month.astype('int32')
    df['Yr']  = df['Dt'].dt.year.astype('int32')
    df['Doy'] = df['Dt'].dt.dayofyear.astype('int32')
    df = df.sort_values('Dt').reset_index(drop=True)

    out_path = os.path.join(OUT_DIR, f'hisCota_{station_code}.pkl')
    df.to_pickle(out_path)
    print(f'  -> {out_path}  ({len(df)} rows, {df["Yr"].min()}-{df["Yr"].max()})')
    print(df.groupby('Yr')['Nivel'].count().to_string())
    return df

#%% Process all three new stations
if __name__ == '__main__':
    for code in ['11400000', '14990000', '17050001']:
        process_station(code)
        print()

#%%
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

#%% 1) Select files to be processed. All files should be in the same input folder
out_folder = "/mnt/c/Projects/NGS_PP_Mamiraua_data/Water_level/fonte_boa_12351000/"
os.chdir(out_folder)

in_files = ['data/cotas_C_12351000.csv']

f = in_files

#%% 2) Set data extraction functions
def extract_level(in_data):
    # Set up for processing
    n_rows = len(in_data)
    stacked_data = pd.DataFrame(columns=['dt', 'value'])
    # Loop over original df to stack data
    for r in range(n_rows):
        row_date = in_data.iloc[r]['Data']
        row_year = row_date.strftime('%Y')
        row_month = row_date.strftime('%m')
        d_vals = in_data.iloc[r, 16:47].values
        d_dates = [f'{row_year}-{row_month}-{day:02d}' for day in range(1, 32)]
        df_temp = pd.DataFrame({'dt': d_dates, 'value': d_vals})
        stacked_data = pd.concat([stacked_data, df_temp], ignore_index=True)
        # Drop NAs that correspond to impossible dates such as Feb 31st
    stacked_data = stacked_data.dropna(subset=['dt'])
    # Add day, month and year columns for filtering
    stacked_data['dy'] = stacked_data['dt'].dt.day
    stacked_data['mn'] = stacked_data['dt'].dt.month
    stacked_data['yr'] = stacked_data['dt'].dt.year
    # Remove Feb 29ths from series because our date system is shit
    stacked_data = stacked_data[(stacked_data['dy'] != 29) | (stacked_data['mn'] != 2)]
    # Sort by date for a neat output
    stacked_data = stacked_data.sort_values(by='dt')

    return(stacked_data)

#%% 3) Process files
for f in in_files:
    #%%
    # Read the CSV data
    in_data_raw = pd.read_csv(f[0], skiprows=12, header=0, sep=";", decimal=",", keep_default_na=False)

    #%% Format input data
    in_data = in_data_raw.copy()
    in_data['Data'] = pd.to_datetime(in_data['Data'], format="%d/%m/%Y")
    in_data = in_data[(in_data['MediaDiaria'] == 1) & (in_data['NivelConsistencia'] == 1)]


    #%% Extract and stack observations
    st_data = extract_level(in_data)

    #%% Save results
    out_name = os.path.join(out_folder, f.replace('.csv', '_daily.csv'))
    st_data.to_csv(out_name, index=False)
    
    #%% Check obs count
    st_data.groupby('yr')['value'].count()

# %%

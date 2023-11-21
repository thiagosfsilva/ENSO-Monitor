#%%
import pandas as pd

#%% 1) Select files to be processed. All files should be in the same input folder
in_files = 'data/cotas_C_12351000.csv'

f = in_files

#%% 2) Set data extraction functions
def extract_level(in_df):
    #%% Set up for processing
    n_rows = len(in_df)
    stacked_data = pd.DataFrame(columns=['Dt', 'Nivel'])
    #%% Loop over original df to stack data
    for r in range(n_rows):
        row_date = in_df.iloc[r]['Data']
        row_year = row_date.strftime('%Y')
        row_month = row_date.strftime('%m')
        d_vals = in_df.iloc[r, 16:47].values
        d_dates = [f'{row_year}-{row_month}-{day:0>2}' for day in range(1, 32)]
        df_temp = pd.DataFrame({'Dt': d_dates, 'Nivel': d_vals})
        stacked_data = pd.concat([stacked_data, df_temp], ignore_index=True)
        # Drop NAs that correspond to impossible dates such as Feb 31st
        stacked_data['Dt'] = pd.to_datetime(stacked_data['Dt'], format="%Y-%m-%d",errors='coerce')
        stacked_data = stacked_data.dropna(subset=['Dt'])
        # Add day, month and year columns for filtering
        stacked_data['Dy'] = stacked_data['Dt'].dt.day
        stacked_data['Mn'] = stacked_data['Dt'].dt.month
        stacked_data['Yr'] = stacked_data['Dt'].dt.year
        stacked_data['Doy'] = stacked_data['Dt'].dt.dayofyear
        # Sort by date for a neat output
        stacked_data = stacked_data.sort_values(by='Dt')

    return(stacked_data)

#%% 3) Process files
for f in [in_files]:
    #%%
    # Read the CSV data
    in_data_raw = pd.read_csv(f, skiprows=12, header=0, sep=";", decimal=",")

    #%% Format input data
    in_data = in_data_raw.copy()
    in_data['Data'] = pd.to_datetime(in_data['Data'], format="%d/%m/%Y")
    in_data = in_data[(in_data['MediaDiaria'] == 1)]
    in_data = in_data.drop('NivelConsistencia',)


    #%% Extract and stack observations
    in_melt = pd.melt(in_data,id_vars=['Data'],value_vars=)


    #st_data = extract_level(in_data)

    #%%Remove February 29th
    st_data = st_data[~((st_data['Dy']==29) & (st_data['Mn']==2))]

    #%% Make sure values are floats
    st_data['Nivel'] = st_data['Nivel'].astype(float)
    
    #%% Trim data to full years: 1978 - 2022
    st_data = st_data[(1978 <= st_data['Yr']) & (st_data['Yr']<=2022)] 
    
    #%% Save results
    out_name = f.replace('.csv', '_daily.csv')
    st_data.to_csv(out_name, index=False)
    out_pickle = "./data/hisCota.pkl"
    st_data.to_pickle(out_pickle)

    #%% Count observations for sanity check
    print(st_data.groupby('Yr')['Nivel'].count())
# %%

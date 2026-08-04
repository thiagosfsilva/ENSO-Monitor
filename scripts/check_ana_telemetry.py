#%%
"""Check ANA telemetry availability for every station in raisg_amz_fluvio_list.csv.

Queries ANA's DadosHidrometeorologicos endpoint for a recent date window per
station and records whether it returned data (telem=1) or an "ErrorTable"
response meaning no telemetry (telem=0). Checkpoints progress to a separate
file every 25 stations so a long run can be inspected or resumed without
losing work.
"""
import time
from datetime import date, timedelta

import pandas as pd
import requests

ANA_URL = 'http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos'
IN_PATH = 'data/raisg_amz_fluvio_list.csv'
CHECKPOINT_PATH = 'data/raisg_amz_fluvio_list_telem_checkpoint.csv'
DELAY_SECONDS = 1
WINDOW_DAYS = 90
TIMEOUT = 30


def has_telemetry(station_code, start, end):
    for attempt in range(2):
        try:
            r = requests.get(
                ANA_URL,
                params={'codEstacao': station_code, 'dataInicio': start, 'dataFim': end},
                timeout=TIMEOUT,
            )
            return 'DadosHidrometereologicos' in r.text
        except requests.RequestException as e:
            print(f'  retry {station_code}: {e}')
            time.sleep(2)
    return None  # could not determine after retries


def main():
    df = pd.read_csv(IN_PATH, dtype={'CodigoEstacao': str})
    end = date.today().strftime('%Y-%m-%d')
    start = (date.today() - timedelta(days=WINDOW_DAYS)).strftime('%Y-%m-%d')

    results = []
    for i, row in df.iterrows():
        code = row['CodigoEstacao']
        ok = has_telemetry(code, start, end)
        telem = 1 if ok else 0
        results.append(telem)
        print(f'[{i + 1}/{len(df)}] {code} ({row["Nome"]}): telem={telem}', flush=True)

        if (i + 1) % 25 == 0 or i == len(df) - 1:
            checkpoint = df.iloc[:len(results)].copy()
            checkpoint['telem'] = results
            checkpoint.to_csv(CHECKPOINT_PATH, index=False)

        time.sleep(DELAY_SECONDS)

    df['telem'] = results
    df.to_csv(IN_PATH, index=False)
    print(f'Done. {sum(results)}/{len(results)} stations have active telemetry.')


#%%
if __name__ == '__main__':
    main()

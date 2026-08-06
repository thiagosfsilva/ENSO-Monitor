#%%
"""Per-station annual minimum/maximum water level tables.

For each station, merges the historical (hisCota) and telemetry (curData)
records the same way plot_level.py does, then writes two CSVs to
data/levels/: years ranked by lowest annual minimum first, and years
ranked by highest annual maximum first.
"""
import re

import pandas as pd

# Mirrors plot_level.py's STATIONS dict — duplicated here (like get_telem.py's
# STATION_CONFIGS) so this script stays runnable standalone as `python
# scripts/level_extremes.py` without needing the project root on sys.path.
STATIONS = {
    '12351000': {'name': 'Fonte Boa',             'telem_start': 2023},
    '11400000': {'name': 'S. P. de Olivenca',     'telem_start': 2026},
    '14990000': {'name': 'Manaus',                'telem_start': 2015},
    '17050001': {'name': 'Obidos',                'telem_start': 2026},
    '13150003': {'name': 'Coari',                 'telem_start': 2025},
    '19500000': {'name': 'Macapa',                'telem_start': 2024},
}

# Years with fewer daily observations than this are excluded — mirrors the
# >=300-point threshold plot_level.py uses to skip partial years (e.g. the
# current year still in progress would otherwise show a misleading extreme).
MIN_YEAR_COVERAGE = 300

OUT_DIR = 'data/levels'


def _slug(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')


def annual_extremes(station_code, telem_start):
    try:
        hisData = pd.read_pickle(f'data/levels/hisCota_{station_code}.pkl').reset_index()
        hisData['Dt'] = pd.to_datetime(hisData['Dt'])
        hisData['Yr'] = hisData['Dt'].dt.year
        hisData['Nivel'] = hisData['Nivel'] / 100
    except FileNotFoundError:
        hisData = pd.DataFrame(columns=['Dt', 'Doy', 'Nivel', 'Yr'])

    parts = [hisData[hisData['Yr'] < telem_start][['Yr', 'Nivel']]]

    try:
        curData = pd.read_pickle(f'data/levels/curData_{station_code}.pkl').reset_index()
        curData['Dt'] = pd.to_datetime(curData['Dt'])
        curData['Yr'] = curData['Dt'].dt.year
        curData['Nivel'] = curData['Nivel'] / 100
        parts.append(curData[curData['Yr'] >= telem_start][['Yr', 'Nivel']])
    except FileNotFoundError:
        pass

    allData = pd.concat(parts).dropna(subset=['Nivel'])

    counts = allData.groupby('Yr')['Nivel'].count()
    valid_years = counts[counts >= MIN_YEAR_COVERAGE].index
    grouped = allData[allData['Yr'].isin(valid_years)].groupby('Yr')['Nivel']

    annual_min = grouped.min().reset_index().rename(columns={'Yr': 'Year', 'Nivel': 'MinLevel_m'})
    annual_max = grouped.max().reset_index().rename(columns={'Yr': 'Year', 'Nivel': 'MaxLevel_m'})
    return annual_min, annual_max


def main():
    for code, cfg in STATIONS.items():
        annual_min, annual_max = annual_extremes(code, cfg['telem_start'])

        annual_min = annual_min.sort_values('MinLevel_m', ascending=True).reset_index(drop=True)
        annual_max = annual_max.sort_values('MaxLevel_m', ascending=False).reset_index(drop=True)

        slug = _slug(cfg['name'])
        min_path = f'{OUT_DIR}/extremes_min_{code}_{slug}.csv'
        max_path = f'{OUT_DIR}/extremes_max_{code}_{slug}.csv'
        annual_min.to_csv(min_path, index=False)
        annual_max.to_csv(max_path, index=False)
        print(f'{code} ({cfg["name"]}): {len(annual_min)} years -> {min_path}, {max_path}')


#%%
if __name__ == '__main__':
    main()

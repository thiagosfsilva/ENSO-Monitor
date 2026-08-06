"""Visualize how each station's annual flood (max) and drought (min) water
levels have diverged from the long-term mean over time.

For each year: a blue bar rises from the historical mean to that year's
maximum level; a red bar falls from the mean to that year's minimum. Each
bar fades from light (at the baseline) to dark (at its tip), and the color
scale is shared across all bars, so a longer bar's tip is objectively
darker than a shorter bar's — the worst floods and droughts stand out at a
glance. Dashed lines mark the 10th-highest flood and 10th-lowest drought,
so the top-10 extreme years are easy to pick out.

Outputs one light and one dark PNG per station, named by station.
"""
import re

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Read directly from the main project's data folder (run this script from
# within amazon_hydro_change_viz/) so figures always reflect the latest
# fetched/processed data instead of a stale local copy.
DATA_DIR = '../data/levels'

# Mirrors plot_level.py's STATIONS dict — duplicated here (like get_telem.py's
# STATION_CONFIGS) so this script stays runnable standalone.
STATIONS = {
    '12351000': {'name': 'Fonte Boa',             'telem_start': 2023},
    '11400000': {'name': 'S. P. de Olivenca',     'telem_start': 2026},
    '14990000': {'name': 'Manaus',                'telem_start': 2015},
    '17050001': {'name': 'Obidos',                'telem_start': 2026},
    '13150003': {'name': 'Coari',                 'telem_start': 2025},
    '19500000': {'name': 'Macapa',                'telem_start': 2024},
}

MIN_YEAR_COVERAGE = 300  # drop partial years (e.g. the current year in progress)
TOP_N = 10

# Sequential ramps derived from the dataviz skill's diverging blue<->red pair,
# each validated as a one-hue ordinal ramp (monotone lightness, >=2:1 light-end
# contrast, single hue) via scratchpad/validate_ramp.py. Both themes read
# light->dark (base to tip), by explicit choice.
BLUE_RAMP = ['#86b6ef', '#5598e7', '#2a78d6', '#1c5cab', '#0d366b']
RED_RAMP = ['#ee8c8c', '#e34948', '#b93838', '#7a2424']

BAR_WIDTH = 0.8
N_GRADIENT_STEPS = 100

THEMES = {
    'light': dict(
        surface='#fcfcfb', text_primary='#0b0b0b', text_secondary='#52514e',
        grid='#e1e0d9', baseline='#898781',
        blue_ramp=BLUE_RAMP, red_ramp=RED_RAMP,
        threshold_blue=BLUE_RAMP[3], threshold_red=RED_RAMP[2],
    ),
    'dark': dict(
        surface='#1a1a19', text_primary='#ffffff', text_secondary='#c3c2b7',
        grid='#2c2c2a', baseline='#383835',
        blue_ramp=BLUE_RAMP, red_ramp=RED_RAMP,
        threshold_blue=BLUE_RAMP[0], threshold_red=RED_RAMP[0],
    ),
}


def _slug(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')


def draw_gradient_bar(ax, x, y_from, y_to, cmap, global_max_delta):
    """Fill a bar from y_from to y_to with a light->dark gradient, where the
    color at each point is set by its absolute distance from y_from on a
    scale shared across every bar — so a longer bar's tip is objectively
    darker than a shorter bar's, not just internally faded."""
    heights = np.linspace(y_from, y_to, N_GRADIENT_STEPS)
    t = np.abs(heights - y_from) / global_max_delta
    colors = cmap(t).reshape(N_GRADIENT_STEPS, 1, 4)
    lo, hi = sorted([y_from, y_to])
    ax.imshow(colors, extent=[x - BAR_WIDTH / 2, x + BAR_WIDTH / 2, lo, hi],
              origin='lower' if y_to >= y_from else 'upper',
              aspect='auto', zorder=2)


def load_series(station_code, telem_start):
    hisData = pd.read_pickle(f'{DATA_DIR}/hisCota_{station_code}.pkl').reset_index()
    hisData['Dt'] = pd.to_datetime(hisData['Dt'])
    hisData['Yr'] = hisData['Dt'].dt.year
    hisData['Nivel'] = hisData['Nivel'] / 100

    curData = pd.read_pickle(f'{DATA_DIR}/curData_{station_code}.pkl').reset_index()
    curData['Dt'] = pd.to_datetime(curData['Dt'])
    curData['Yr'] = curData['Dt'].dt.year
    curData['Nivel'] = pd.to_numeric(curData['Nivel'], errors='coerce') / 100

    parts = [
        hisData[hisData['Yr'] < telem_start][['Dt', 'Yr', 'Nivel']],
        curData[curData['Yr'] >= telem_start][['Dt', 'Yr', 'Nivel']],
    ]
    data = pd.concat(parts).dropna(subset=['Nivel']).sort_values('Dt').reset_index(drop=True)
    data['Nivel'] = data['Nivel'].astype(float)
    return data


def decade_ticks(year_min, year_max):
    start = (year_min // 10) * 10
    end = ((year_max // 10) + 1) * 10
    boundaries = list(range(start, end + 1, 10))
    centers = [d + 5 for d in boundaries[:-1]]
    labels = [f'{d}s' for d in boundaries[:-1]]
    return boundaries, centers, labels


def build_figure(annual, overall_mean, year_range, theme, out_path):
    t = THEMES[theme]
    blue_cmap = LinearSegmentedColormap.from_list('flood', t['blue_ramp'])
    red_cmap = LinearSegmentedColormap.from_list('drought', t['red_ramp'])

    global_max_flood = annual['flood_delta'].max()
    global_max_drought = annual['drought_delta'].max()

    flood_top10 = annual['max'].nlargest(TOP_N).min()
    drought_top10 = annual['min'].nsmallest(TOP_N).max()

    fig, ax = plt.subplots(figsize=(18, 7))

    xlim = (annual['Yr'].min() - 1, annual['Yr'].max() + 1)
    ylim = (annual['min'].min() - 0.5, annual['max'].max() + 0.5)

    boundaries, centers, labels = decade_ticks(*year_range)
    for b in boundaries:
        if xlim[0] <= b <= xlim[1]:
            ax.axvline(b, color=t['grid'], linewidth=1, zorder=1)
    ax.set_xticks(centers)
    ax.set_xticklabels(labels)

    for _, row in annual.iterrows():
        draw_gradient_bar(ax, row['Yr'], overall_mean, row['max'], blue_cmap, global_max_flood)
        draw_gradient_bar(ax, row['Yr'], overall_mean, row['min'], red_cmap, global_max_drought)

    ax.hlines(flood_top10, *xlim, color=t['threshold_blue'], linewidth=1, linestyle=(0, (5, 3)), zorder=3)
    ax.hlines(drought_top10, *xlim, color=t['threshold_red'], linewidth=1, linestyle=(0, (5, 3)), zorder=3)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.hlines(overall_mean, *xlim, color=t['baseline'], linewidth=1, zorder=3)

    ax.set_ylabel('Water Level (m)', color=t['text_secondary'])
    ax.set_xlabel('Decade', color=t['text_secondary'])

    ax.grid(axis='y', color=t['grid'], linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(t['baseline'])
    ax.tick_params(colors=t['text_secondary'])

    fig.patch.set_facecolor(t['surface'])
    ax.set_facecolor(t['surface'])
    plt.tight_layout()

    plt.savefig(out_path, dpi=150, facecolor=t['surface'])
    plt.close(fig)
    print(f'Saved {out_path}')


def main():
    for station_code, cfg in STATIONS.items():
        data = load_series(station_code, cfg['telem_start'])

        counts = data.groupby('Yr')['Nivel'].count()
        valid_years = counts[counts >= MIN_YEAR_COVERAGE].index
        valid = data[data['Yr'].isin(valid_years)]

        overall_mean = data['Nivel'].mean()

        annual = valid.groupby('Yr')['Nivel'].agg(['min', 'max']).reset_index()
        annual['flood_delta'] = (annual['max'] - overall_mean).clip(lower=0)
        annual['drought_delta'] = (overall_mean - annual['min']).clip(lower=0)

        year_range = (data['Yr'].min(), data['Yr'].max())
        slug = _slug(cfg['name'])

        for theme in THEMES:
            out_path = f'{slug}_extremes_change_{theme}.png'
            build_figure(annual, overall_mean, year_range, theme, out_path)


if __name__ == '__main__':
    main()

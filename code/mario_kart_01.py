import pydytuesday
import pandas as pd
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
from pyfonts import load_google_font
from highlight_text import fig_text, ax_text
import matplotlib.patheffects as path_effects

url = "https://raw.githubusercontent.com/JosephBARBIERDARNAL/data-matplotlib-journey/refs/heads/main/mariokart/mariokart.csv"


df_mario = pl.read_csv(url)
df_mario = df_mario.with_columns(
    year = pl.col("date").cast(pl.Date).dt.year()
)

tracks = df_mario['track'].unique()
tracks=tracks.sort(descending=True).to_list()
track_to_index = {track: idx for idx, track in enumerate(tracks)}
df_mario = df_mario.with_columns(
    pl.col('track').replace(track_to_index).alias('track_index')
)


def jitter(df, col, amount=0.4):
    return df[col].to_numpy().astype(float) + np.random.uniform(-amount, amount, len(df))

df_mario = df_mario.with_columns(
    track_index_jitter = jitter(df_mario, 'track_index'), 
    shortcut_flag = pl.when(pl.col('shortcut') == 'Yes')
     .then(0.5)
     .otherwise(0.0)
)

print(df_mario)


df_mario = df_mario.filter(pl.col('type') == 'Three Lap')
df_mario = df_mario.sort('track', descending=True)





mario_colors = [
    '#F6D358', # yellow
    '#AD332D',
    '#939FAF',
    '#477333',
    '#CE4C26',
    '#8A8E7F',
    '#E9C076',
    '#8A8E80',
    '#FAED86',
    '#B9F973',    
    '#edeada',
    '#100f24',
    '#5d8d60',
    '#c74634',
    '#e55d82',    
    '#409edb',
    '#e8bd00',
    '#7b6500',
    '#dd2020', 
    '#fad2a8',  
    '#9C5335'
]
from pypalettes import load_cmap
cmap = load_cmap("FridaKahlo").colors

ft_Silkscreenont = load_google_font("Silkscreen")
ft_VT323 = load_google_font("VT323")
df_PressStart = load_google_font("Press Start 2P")

df_mario = df_mario.to_pandas()
print(df_mario)

# Plot ------------------------------------------------> #

# layout = [['title'], 
#           ['left']
#     ]
# fig, axs = plt.subplot_mosaic(
#                 layout,
#                 figsize=(6,8), 
#                 dpi=300,
#                 facecolor=cmap[2],
#                 gridspec_kw={'height_ratios': [1,99],
#                             'width_ratios': [1],
#                             'wspace': 0
#                             }
#     )

fig, ax = plt.subplots(figsize=(3, 4), dpi=1000, facecolor=cmap[2])
# Left Side

ax.set_facecolor(cmap[2])

ax.scatter(df_mario.time, 
           df_mario.track_index_jitter, 
           alpha=0.9, 
           s=2, 
           color=cmap[1], 
           edgecolors=cmap[-1], 
           linewidths=df_mario.shortcut_flag)

ax.set_yticks(np.arange(len(tracks)))
ax.set_yticklabels(tracks, fontproperties=ft_VT323)
ax.tick_params(axis='y', length=0)
ax.tick_params(labelsize=8)
ax.set_yticklabels(tracks, fontproperties=ft_VT323, fontsize=6)

time_label = ['0s', '50s', '100s', '150s', '200s', '250s', '300s', '350s']
ax.set_xticks(np.arange(8)*50)
ax.set_xticklabels(time_label, fontproperties=ft_VT323, fontsize=6)
ax.tick_params(axis='x', length=0)

ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)

for label in ax.get_yticklabels():
    label.set_fontsize(8)
    label.set_fontweight('normal')

# top  plot
# ax = axs['title']
# ax.set_facecolor(cmap[3])
# ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
# ax.set_xticks([])
# ax.set_yticklabels([])
# ax.tick_params(axis='y', length=0)


# fig_text(
#    s='Mario Kart Records by Rrack',
#    x=0.45, y=0.95, fontsize=16,
#    ha='center', color=cmap[0],
#    font=df_PressStart, fig=fig
# )
fig.tight_layout()
fig.savefig('plots/MarioKart-Finish-01.png')
# plt.show()



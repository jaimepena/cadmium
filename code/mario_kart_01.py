import pandas as pd
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
from pyfonts import load_google_font
from highlight_text import fig_text, ax_text
import matplotlib.patheffects as path_effects
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches


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


from pypalettes import load_cmap
cmap = load_cmap("FridaKahlo").colors
m = [
    ''
]

mario_colors = [
    "#f2f6a7",
    '#E5341D',
    '#12AE00',
    '#FFFFB4',
    "#F7B500",  # yellow amber
    '#D20303',  # traffice light red
]

def jitter(df, col, amount=0.30):
    return df[col].to_numpy().astype(float) + np.random.uniform(-amount, amount, len(df))

df_mario = df_mario.with_columns(
    track_index_jitter = jitter(df_mario, 'track_index'), 
    shortcut_flag = pl.when(pl.col('shortcut') == 'Yes')
     .then(0.5)
     .otherwise(0.0),
    shortcut_flag_color = pl.when(pl.col('shortcut') == 'Yes')
     .then(pl.lit(mario_colors[5]))
     .otherwise(pl.lit(mario_colors[2]))
)


df_mario = df_mario.filter(pl.col('type') == 'Three Lap')
df_mario = df_mario.sort('track', descending=True)


notoEmoji = load_google_font("Noto Emoji")
ft_Silkscreenont = load_google_font("Silkscreen")
ft_VT323 = load_google_font("VT323")
df_PressStart = load_google_font("Press Start 2P")


df_mario = df_mario.to_pandas()

# Plot ------------------------------------------------> #

fig, ax = plt.subplots(figsize=(4.5, 6), dpi=300, facecolor=mario_colors[0])
# Left Side

ax.set_facecolor(mario_colors[0])

ax.scatter([], [], color=mario_colors[1], label='Shortcut', s=20, edgecolors='white', linewidths=0.5)
ax.scatter([], [], color=mario_colors[2], label='No Shortcut', s=20, edgecolors='white', linewidths=0.5)

ax.scatter(df_mario.time, 
           df_mario.track_index_jitter, 
           alpha=1, 
           s=4, 
           color=df_mario.shortcut_flag_color,
           edgecolors='white', 
           linewidths=0.04
)

ax.set_yticks(np.arange(len(tracks)))
ax.tick_params(axis='y', length=0)
ax.tick_params(labelsize=6)
ax.set_yticklabels(tracks, fontproperties=ft_VT323, fontsize=8)

time_label = ['0 seconds', '50s', '100s', '150s', '200s', '250s', '300s', '350s']
ax.set_xticks(np.arange(8)*50)
ax.set_xticklabels(time_label, fontproperties=ft_VT323, fontsize=8)
ax.tick_params(axis='x', length=0)

ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)

ax.grid(True, which='major', axis='y', 
        color=mario_colors[5], 
        linestyle='--', linewidth=0.3, alpha=0.5)

# Add the legend
ft_Silkscreenont.set_size(4)
legend = ax.legend( loc='best', 
                    frameon=False, 
                    prop=ft_Silkscreenont)
legend.get_frame().set_facecolor('none')




fig.patches.extend([
    # Inner black rectangle with silver border
    patches.Rectangle(
        (.15, 0.828),
        .70,
        0.17,
        transform=fig.transFigure,
        facecolor='black',
        edgecolor='#ABABD3',  # Silver border
        linewidth=0.5,
        zorder=-1
    ),
    # Outer rectangle with shiny border, slightly larger
    patches.Rectangle(
        (.147, 0.825),        # Slightly offset to surround the first
        .706,                  # Slightly wider
        0.176,                 # Slightly taller
        transform=fig.transFigure,
        facecolor='none',     # Transparent fill
        edgecolor='#ABABD3',  # Shiny border
        linewidth=1,
        zorder=-1
    )
])


fig.suptitle(
    "Super\nMario Kart",
    fontproperties=df_PressStart,
    fontsize=14,
    color='#DBDBEE',
    path_effects=[path_effects.Stroke(linewidth=1.4, foreground='#7E7CA1'), path_effects.Normal()]
)

fig.text(0.35, 0.965, "🍄", 
         fontproperties=notoEmoji, 
         fontsize=14, 
         ha='center', 
         va='center', 
         color=mario_colors[2],
         transform=fig.transFigure, 
         zorder=10)

fig.text(0.641, 0.965, "🍄", 
         fontproperties=notoEmoji, 
         fontsize=14, 
         ha='center', 
         va='center', 
         color=mario_colors[1],
         transform=fig.transFigure, 
         zorder=10)

# ft_Silkscreenont.set_size(5)
# text = fig.text(0.40, .87, "These are the top speedrun records by course.", 
#         color=mario_colors[2], 
#         ha='center', 
#         va='top',
#         fontproperties=ft_Silkscreenont,
#         transform=fig.transFigure, 
#         zorder=10)

ft_VT323.set_size(9)
fig_text(
    s="<These are the top speedrun records by course.>\n<       Shortcuts>< are key to faster times.>",
    highlight_textprops=[
        {'color': '#DBDBEE', 'fontproperties': ft_VT323},
        {'color': mario_colors[1], 'fontproperties': ft_VT323},
        {'color': '#DBDBEE', 'fontproperties': ft_VT323}
    ],
    x=0.5, y=0.88,
    ha='center',
    va='top',
    fig=fig,
    transform=fig.transFigure, 
    zorder=999
)


fig.text(
    0.01, 0.01,  # Bottom left corner
    "Source: Mario Kart World Records site",
    color="#888888",  # Subtle gray
    fontsize=6,
    ha='left',
    va='bottom',
    fontproperties=ft_VT323,  # Or any font you prefer
    transform=fig.transFigure,
    zorder=1000
)

fig.tight_layout()
plt.subplots_adjust(top=0.80)
fig.savefig('plots/MarioKart-Finish-01.png')
#plt.show()




# fig_text(
#     s="<🍄><Super Mario Kart><🍄>",
#     highlight_textprops=[
#         {'fontproperties': notoEmoji, 'fontsize': 22},  # left emoji
#         {'color': 'white', 'fontsize': 16, 'fontweight': 'bold', 'fontproperties': df_PressStart,
#          'path_effects': [path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()]},  # title
#         {'fontproperties': notoEmoji, 'fontsize': 22}   # right emoji
#     ],
#     x=0.5, y=0.93,  # Adjust y for vertical position in the banner
#     ha='center',
#     va='center',
#     fig=fig,
#     zorder=20
# )
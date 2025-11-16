import pydytuesday
import pandas as pd
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
from pyfonts import load_google_font
from pypalettes import load_cmap
import matplotlib.ticker as mticker
import re
from drawarrow import ax_arrow
from adjustText import adjust_text
from highlight_text import fig_text, ax_text

url = "https://raw.githubusercontent.com/JosephBARBIERDARNAL/data-matplotlib-journey/refs/heads/main/footprint/footprint.csv"

df = pl.read_csv(url)

region = df.select(pl.col('region').unique()).to_series().to_list()
country = df.select(pl.col('country').unique()).to_series().to_list()
print(df)
cmap = load_cmap("VanGogh2").colors
print(cmap)

#font = load_google_font("Geologica")

region_color_map = dict(zip(region, cmap))


df = df.with_columns(
    pl.col('region').replace(region_color_map).alias('colors'), 
    deficit_surplus = (pl.col('biocapacity') - pl.col('footprint'))/pl.col('biocapacity')
)

df = df.with_columns(
    deficit_rank = pl.col('deficit_surplus').rank('dense', descending=False),
    surplus_rank = pl.col('deficit_surplus').rank('dense', descending=True),
    population_rank = pl.col('populationMillions').rank('dense', descending=True)
)

df = df.with_columns(
    top_countries = (pl.col('deficit_rank') <= 10) | (pl.col('surplus_rank') <= 10),
    colors = pl.when((pl.col('deficit_rank') <= 10) | (pl.col('surplus_rank') <= 10) )
              .then(
                  pl.when(pl.col('deficit_surplus') < 0)
                    .then(pl.lit(f'{cmap[0]}'))
                    .otherwise(pl.lit(f'{cmap[4]}'))
              )
              .otherwise(pl.lit('lightgray'))
)

df = df.sort('footprint', descending=False)
df = df.filter(pl.col('deficit_rank') <= 25)
#print(df.columns)
df = df.to_pandas()

# Plot ------------------------------------------------> #

layout = [['title', 'title', 'title'], 
          ['left', 'right', 'pct'],
          ['notes', 'notes', 'notes']]
fig, axs = plt.subplot_mosaic(
                layout,
                figsize=(5,8), 
                dpi=300,
                gridspec_kw={'height_ratios': [.5, 12, 0.1],
                            'width_ratios': [1, 1, .01],
                            'wspace': 0
                            }
    )

# left bar plot
ax_left = axs['left']
ax_left.barh(df.country, 
        df.footprint, 
        color=cmap[0])
ax_left.invert_xaxis()
ax_left.set_ylabel('')
ax_left.tick_params(axis='y', length=0)
ax_left.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax_left.set_xticks([])
ax_left.set_xlim(df.footprint.max() * 1.05, 0)

for i, v  in enumerate(df.footprint):
    ax_left.text(v-0.4, i, f"{v:,.1f}", va='center', ha='left', fontsize=6, color='white', fontweight='bold')

# for i, v  in enumerate(df.deficit_surplus):
#     ax_left.text(df.footprint.max() * 1.2, i, f"{v*100:.1f}%", va='center', ha='left', fontsize=6, color='black', fontweight='bold')


for label in ax_left.get_yticklabels():
    label.set_fontsize(6)
    label.set_fontweight('normal')

# right bar plot
ax_right = axs['right']
ax_right.barh(df.country, 
        df.biocapacity, 
        color=cmap[4])
ax_right.set_ylabel('')
ax_right.tick_params(axis='y', length=0)
ax_right.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax_right.set_xticks([])
ax_right.set_yticklabels([])
ax_right.set_xlim(0, df.footprint.max() * 1.05)

for i, v  in enumerate(df.biocapacity):
    ax_right.text(v+0.4, i, f"{v:,.1f}", va='center', ha='left', fontsize=6, color='black', fontweight='bold')


# pct plot
ax_pct = axs['pct']
ax_pct.set_ylabel('')
ax_pct.tick_params(axis='y', length=0)
ax_pct.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax_pct.set_xticks([])
ax_pct.set_yticklabels([])

ax_pct.barh(df.country, 
        df.deficit_surplus, 
        alpha=0)

for i, v  in enumerate(df.deficit_surplus):
    ax_pct.text(1, i, f"{v*100:.1f}%", va='center', ha='left', fontsize=6, color='black')

# top  plot
ax_title = axs['title']
ax_title.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax_title.set_xticks([])
ax_title.set_yticklabels([])
ax_title.tick_params(axis='y', length=0)

ax_text(0.2,0, '<Footprint>< to ><Biocapacity>< Deficit>\n<Top 25 Countries >',
    highlight_textprops=[{'color': 'red', 'fontsize':11, 'fontweight':'bold'},
    {'color': 'black', 'fontsize':11, 'fontweight':'bold'},
    {'color': 'green', 'fontsize':11, 'fontweight':'bold'},
    {'color': 'black', 'fontsize':11, 'fontweight':'bold'},
    {'color': 'black', 'fontsize':11, 'fontweight':'bold'}],
    ax=ax_title,
    ha='center',
    transform=ax_title.transAxes
)
# notes  plot
ax_notes = axs['notes']
ax_notes.set_ylabel('')
ax_notes.tick_params(axis='y', length=0)
ax_notes.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax_notes.set_xticks([])
ax_notes.set_yticklabels([])
ax_notes.tick_params(axis='y', length=0)
ax_notes.set_xlim(0,1)

ax_notes.text(
   -0.25, 
    0, 
    'Source: Global Footprint Network',
    color='gray',
    fontweight='normal',
    fontsize=6.5,
    ha='left',
    va='bottom',
    transform=ax_notes.transAxes
)

# save plot
fig.tight_layout()


fig.savefig('plots/Eco-Sustainability-Line-02.png')
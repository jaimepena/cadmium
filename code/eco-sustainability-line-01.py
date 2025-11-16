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

url = "https://raw.githubusercontent.com/JosephBARBIERDARNAL/data-matplotlib-journey/refs/heads/main/footprint/footprint.csv"

df = pl.read_csv(url)

region = df.select(pl.col('region').unique()).to_series().to_list()
country = df.select(pl.col('country').unique()).to_series().to_list()
print(country)
cmap = load_cmap("VanGogh2").colors
print(cmap)

font = load_google_font("Geologica")

region_color_map = dict(zip(region, cmap))
for r, c in region_color_map.items():
    print(f"{r}: {c}")

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

print(df['populationMillions', 'country'])
df = df.to_pandas()

golden_ratio = 1.618
height = 5
width = round(height * golden_ratio, 2)
fig, ax = plt.subplots(figsize=(width, height), dpi=300)

bubble=ax.scatter( 
        df.footprint, 
        df.biocapacity,
        s=df.populationMillions*10, 
        c=df.colors, 
        alpha=0.7, 
        edgecolors='gray', 
        linewidths=0.3)


texts = []
for i, row in df.loc[((df.deficit_rank <= 10) | (df.surplus_rank <= 10)  )].iterrows():
    jitter_x = np.random.uniform(-0.01, 0.01)  # Random offset between -0.5 and 0.5
    jitter_y = np.random.uniform(-0.01, 0.01)
    texts.append(ax.text(
        row['footprint'] ,
        row['biocapacity'] ,
        row['country'],
        fontsize=7,
        font=font
    ))

# Filter to only adjust specific countries
countries_to_adjust = ['Guyana', 'Belgium', 'French Polynesia']
texts_to_adjust = [
    text for text in texts 
    if text.get_text() in countries_to_adjust
]

# Only adjust the filtered texts
adjust_text(
    texts_to_adjust,  # Only these will be adjusted
    ax=ax,
    arrowprops=dict(arrowstyle="->", color='gray', lw=0.5)
)

xlims = ax.get_xlim()
ylims = ax.get_ylim()
max_value = max(xlims[1], ylims[1])
diagonal_range = np.linspace(0, max_value, 100)
ax.plot(diagonal_range, diagonal_range, 'r--', linewidth=1, label='Sustainability Line')

ax.grid(axis="both", which="both", ls="dotted", lw=0.2, zorder=-1)

ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.set_xlim(right=15)
ax.set_yscale('symlog')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(labelsize=6)
ax.set_facecolor("#fdfdfc")

ax.set_xlabel("Ecological Footprint", font=font, size=8)
ax.set_ylabel("Biocapacity (Log)", font=font, size=8)

ax.tick_params(axis='x', colors='gray')
ax.tick_params(axis='y', colors='gray')
ax.spines['bottom'].set_color('gray')  # x-axis line
ax.spines['left'].set_color('gray')    # y-axis line

ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])
ax.set_xticklabels(["", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

ax.set_yticks([1,2,5,10,25,50, 100])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y)))




handles, labels = bubble.legend_elements(
          prop="sizes", 
          alpha=0.1,
          num=3
          )

# Extract numbers from LaTeX strings and divide by 10
def extract_number(label):
    match = re.search(r'\d+', label)
    return int(match.group()) if match else label

labels = [str(extract_number(l)//10) for l in labels]

ax.legend(handles, labels, title="Population (M)", title_fontsize=6 ,
          loc='upper right', fontsize=4, framealpha=0)

ax_arrow(
    tail_position=(9.5, 4.5),
    head_position=(8.3, 5),
    width=1,
    radius=0.3,
    color="darkred"
)
ax.text(9.5, 4.5, 'United States', font=font, size=7)




text = ax.text(0.29, .98, "Top 10 Countries ", 
               color="black", 
               ha='center', 
               va='top',
               fontproperties=font,
               transform=fig.transFigure )
# Subsequent words, positioned with annotate(), relative to the preceding one.
common_annotate_args = {
    "xycoords": text,
    "xy": (1, 0),
    "verticalalignment": "bottom",
    "fontproperties": font
}
text = ax.annotate(
    "Above", 
    color="green", weight="bold", 
     xycoords=text, xy=(1, 0), verticalalignment="bottom", fontproperties=font
   ) 
text = ax.annotate(
    "|", 
    color="black",
    xycoords=text, xy=(1, 0), verticalalignment="bottom", fontproperties=font
   ) 
text = ax.annotate(
    "Below ", 
    color="red", weight="bold", 
     xycoords=text, xy=(1, 0), verticalalignment="bottom", fontproperties=font
   )
text = ax.annotate(
    "The Ecological Sustainability Line", 
    color="black",  
     xycoords=text, xy=(1, 0), verticalalignment="bottom", fontproperties=font
   )


txt = """The Ecological Sustainability Line is a conceptual boundary that represents the point at 
which a population's ecological footprint (the demand placed on nature for resources and 
waste absorption) exactly matches the region's biocapacity (nature's supply of renewable 
resources and services)."""
fig.text(0.5, 0.94, txt, 
         fontproperties=font, fontsize=6, ha='center', va='top', 
         color='black', wrap=True, transform=fig.transFigure)

# Add source text at bottom right
fig.text(0.1, 0.05, 'Source: Global Footprint Network', 
         fontproperties=font, fontsize=6, ha='left', va='bottom', color='gray', transform=fig.transFigure)

plt.subplots_adjust(top=0.84)

fig.savefig('plots/Eco-Sustainability-Line-01.png')
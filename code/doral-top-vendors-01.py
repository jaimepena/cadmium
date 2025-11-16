import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import pandas as pd
from pyfonts import load_google_font
from pyspark.sql import SparkSession, Window, functions as F, types as T
import os

spark = SparkSession.builder \
    .appName("Read file") \
    .getOrCreate()
df = spark.read.csv('data/checkbook_data_2025-09-23-2.csv', header=True, 
                    inferSchema=True)


# October 01, 2024 - September 30, 2025  -->2025
# October 01, 2023 - September 30, 2024  -->2024
# October 01, 2022 - September 30, 2023  -->2023
# October 01, 2021 - September 30, 2022  -->2022
df = df.withColumn('Payment Year', 
                   F.when(F.month('Check Date')>= 10,
                          F.year('Check Date') + 1)
                          .otherwise(F.year('Check Date')))

window_spec = Window.partitionBy('Payment Year').orderBy(F.col('Amount').desc())

df_pandas = (df
 .groupBy(['Payment Year', 'Vendor'])
 .agg(F.sum('Amount')
      .alias('Amount'))
 .orderBy(['Payment Year', 'Amount'], ascending=[1, 0])
 .withColumn('Rank', F.row_number().over(window_spec))
 .withColumn('Vendor', F.when(F.col('Rank') > 10, 'Other').otherwise(F.col('Vendor')))
 .withColumn('Rank', F.when(F.col('Rank') > 10, 11).otherwise(F.col('Rank')))
 .groupBy(['Payment Year', 'Vendor', 'Rank'])
 .agg(F.sum('Amount').alias('Amount'))
 .orderBy(['Payment Year', 'Rank'], ascending=[1, 0])
 ).toPandas()

print(df_pandas)

plt.style.use('stylesheets/stylesheet-01.mplstyle')

fig, axs = plt.subplots(2, 2, figsize=(24, 12), dpi=300)

font = load_google_font("Alfa Slab One")

years = [2025, 2024, 2023, 2022]
for ax, year in zip(axs.flat, years):
    df_subset = df_pandas.query(f" `Payment Year` == {year} ")
    c = df_subset.Vendor.str.startswith('KAUFMAN').map({True: "#578F79", False: '#685e96'})
    ax.barh(df_subset.Vendor, df_subset.Amount, color=c)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x*1e-6:.1f}M'))
    ax.text(0.5, 0.5, F"{year}", transform = ax.transAxes, fontsize=24, font=font, alpha=.50, color='#685e96')
    for i, (v, vendor) in enumerate(zip(df_subset.Amount, df_subset.Vendor)):
        ax.text(v + 100000, i, f'{v*1e-6:.1f}M', va='center', ha='left')

        if vendor.startswith('KAUFMAN') and year >2022:
          label = "Doral Central Park (DCP) Project"  
        elif vendor.startswith('KAUFMAN') and year == 2022:
          label = "DCP"  
        else:
          label = ""

        ax.text(250000, i, label, va='center', ha='left', fontsize=12, font=font, alpha=.99, color="#ffffff")

plt.suptitle("Top Vendors for the City of Doral 2022-2025", fontsize=32, font=font, alpha=.85, color='#685e96')
plt.figtext(0.01, 0.01, "Source: City of Doral Transparency Site"
            , color="#578F79"
            , ha="left" )
fig.tight_layout()
fig.savefig('plots/Top_Vendors_by_Year.png', dpi=300)

# mt.set_theme("default")





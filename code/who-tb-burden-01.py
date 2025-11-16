# Using Python
# Option 1: pydytuesday python library
## pip install pydytuesday

import pydytuesday
import pandas as pd
from pyspark.sql import SparkSession, Window, functions as F, types as T
import requests
import os
import shutil

# Download files from the week, which you can then read in locally
pydytuesday.get_date('2025-11-18')

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Move the downloaded file to data folder
if os.path.exists('who_tb_data.csv'):
    shutil.move('who_tb_data.csv', 'data/who_tb_data.csv')


# Read with PySpark
spark = SparkSession.builder \
    .appName("Read file") \
    .getOrCreate()

who_tb_data = spark.read.csv('data/who_tb_data.csv', header=True, inferSchema=True)
who_tb_data.show(10)
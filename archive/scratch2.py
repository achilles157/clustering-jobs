import pandas as pd
import json

df=pd.read_csv('data/java_job_market_hubs_final.csv')
with open('data/java_regencies.geojson') as f:
    g=json.load(f)

master=set([f['properties']['clean_name'] for f in g['features']])
df_set=set(df['matched_regency'].unique())
print('DF minus Master:', df_set - master)
print('Master minus DF:', master - df_set)

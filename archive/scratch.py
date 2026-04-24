import pandas as pd
import json

df = pd.read_csv('data/integrated_job_market_java_v2.csv')
df['m'] = df['matched_regency'].apply(lambda x: str(x).strip() if str(x).strip().startswith(('Kota', 'Administrasi')) else f'Kabupaten {str(x).strip()}')

with open('data/java_regencies.geojson') as f:
    g = json.load(f)

master = set([f['properties']['clean_name'] for f in g['features']])
m_set = set(df['m'].unique())
print('In data but not in master:')
print(m_set - master)

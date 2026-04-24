import pandas as pd
import json
import plotly.express as px

df = pd.read_csv('data/java_job_market_hubs_final.csv')
with open('data/java_regencies.geojson') as f:
    g = json.load(f)

for feature in g['features']:
    feature['id'] = feature['properties']['clean_name']

try:
    fig = px.choropleth_map(
        df, 
        geojson=g, 
        locations='matched_regency', 
        featureidkey='id', 
        color='opportunity_index', 
        center={'lat':-7.2, 'lon':110}, 
        map_style='carto-darkmatter', 
        zoom=6
    )
    fig.write_image('test_map.png', engine='kaleido', width=800, height=600)
    print('Saved')
except Exception as e:
    print(f"Error drawing map: {e}")

import json
with open('data/java_regencies.geojson') as f:
    g = json.load(f)
master = set([f['properties']['clean_name'] for f in g['features']])
print(sorted(list(master))[:10])

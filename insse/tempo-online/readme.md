insse.ro/[tempo-online](http://statistici.insse.ro:8077/tempo-online)  

[dev notes](dev-notes.md) 

- [ ] fetch index
- [ ] download csvs
- [ ] refactor csvs -> db
- [ ] dashboard / charts


Scripts
-[x] 1fetch-context.py →  context.csv
-[x] 2fetch-dataset-list.py → datasets.csv - loops context.csv and fetches dataset lists
-[x] 3fetch-meta → data/meta/<datasetId>.json
-[ ] 4fetch-csvs - downloads csvs
-[ ] 5clean-csvs → database structure

ignored columns and conversion rules in config.json - with converters per dataset or individual receipes/<datasetId>.json

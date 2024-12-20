
<mark>ARCHIVED</mark> &rarr; moved to [tempo-ins-dump](https://github.com/gov2-ro/tempo-ins-dump) 

---

[https://tempo-online.gov2.ro/](tempo-online.gov2.ro) - scrapes data from insse/[tempo-online](http://statistici.insse.ro:8077/tempo-online)  

## Scripts

- `1-fetch-context.py` - fetches contexts &rarr; _data/1-indexes/**\<lang\>**/context.csv_ 
- `2-fetch-matrices.py` - fetches datasets &rarr; _data/1-indexes/**\<lang\>**/matrices.csv_
- `3-fetch-meta.py` - reads _matrices.csv_ and fetches dataset meta json &rarr; _data/2-metas/**\<lang\>**/**\<dataset-id\>**.json_
- `4-varstats-db.py` - parses downloaded dataset meta and saves fields to SQLite.db
- `5-fetch-csv.py` - loops through metas jsons and downloads dataset as csv &rarr; _data/3-datasets/**\<lang\>**/**\<dataset-id\>**.csv_
- `6-data-compactor.py` – compact csv dimensions - replace `opt_label` with `nomItemId` reference
- `0-tempoins-fetch-indexes.py` - fetches ctgs and datasets from prev version: [tempoins](http://statistici.insse.ro/tempoins/) - with archived datasets
- `browser/` - alpha GUI (to be deprecated for [Evidence](https://evidence.dev))


## Roadmap 
### alpha
- [x] fetch index
- [x] download csvs
- [x] refactor csvs -> db
- [x] dashboard / charts (alpha)
- [x] compact data

### beta
- [ ] categorise filters
- [ ] auto charts
- [ ] dataset filtering, charting options

-----

see also [dev notes](dev-notes.md), [metadata](http://80.96.186.4:81/metadata/public.htm) 



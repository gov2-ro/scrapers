see [dev notes](https://docs.google.com/document/d/1FY_1Bb2RF8JGoplnBvvIBTN-PkCfYnGR) / gDoc

------

<mark>obsolete</mark>

`1fetch-context.py` → context.csv → `3fetch-dataset-list.py` → context/<id>.json
`2fetch-matrices.py` → matrices.csv → `4fetch-meta.py` → matrices/<id>.json → `5db.py` →  datasets.db → `6fetch-table.py`

more like:
`2fetch-matrices.py` → matrices.csv → `4fetch-meta.py` → matrices/<id>.json → `6fetch-table-csv.py` → datasets csvs

context→ code == matrices→code
used for datasets hierarchy 

context/<context-id>.json keeps relationships between ctgs/parents and data in matrices/<matrix-id>.json

ignored columns and conversion rules in config.json - with converters per dataset or individual receipes/<datasetId>.json


`6fetch-table.py`

- fetch http://statistici.insse.ro:8077/tempo-ins/matrix/<matrix_id>
- payload data/sample-payload.js
- detect too many rows
- combine requests
- save response html
- extract data

## datasets.db

### fields

CREATE TABLE fields (
        fileid TEXT,
        dim_label TEXT,
        dimCode INTEGER,
        opt_label TEXT,
        nomItemId INTEGER,
        offset INTEGER,
        parentId INTEGER
    )

### datsets

CREATE TABLE datasets (
        filename TEXT,
        ancestors_1_code TEXT,
        ancestors_2_code TEXT,
        ancestors_3_code TEXT,
        ancestors_4_code TEXT,
        matrixName TEXT,
        periodicitati TEXT,
        definitie TEXT,
        ultimaActualizare TEXT,
        metodologie TEXT,
        observatii TEXT,
        persoaneResponsabile TEXT,
        intrerupere_lastPeriod TEXT,
        continuareSerie TEXT,
        nomJud INTEGER,
        nomLoc INTEGER,
        matMaxDim INTEGER,
        matUMSpec INTEGER,
        matSiruta INTEGER,
        matCaen1 INTEGER,
        matCaen2 INTEGER,
        matRegJ INTEGER,
        matCharge INTEGER,
        matViews INTEGER,
        matDownloads INTEGER,
        matActive INTEGER,
        matTime INTEGER
    )
 



- 1fetch-context.py →  context.csv

- 2fetch-dataset-list.py → datasets.csv
loops context.csv and fetches dataset lists

- 3fetch-meta → data/meta/<datasetId>.json

- 4fetch-csvs - downloads csvs

- 5db 

- 5clean-csvs → database structure
config.json - with converters per dataset
or individual receipes/<datasetId>.json
ignored columns




### Roadmap

- [x] fetch index
- [ ] fetch sub-index (dataset lists)
- [ ] download csvs
- [ ] refactor csvs -> db
- [ ] dashboard / charts



### Fetch Index


### Fetch CSV

[tempo-ins/pivot ](http://statistici.insse.ro:8077/tempo-ins/pivot ) 


- encQuery | based on definitions
- matCode | datasetId
- matMaxDim
- matUMSpec
- matRegJ

    curl 'http://statistici.insse.ro:8077/tempo-ins/pivot' \
    -H 'Accept: application/json, text/plain, */*' \
    -H 'Accept-Language: en-GB,en;q=0.8' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/json' \
    -H 'Origin: http://statistici.insse.ro:8077' \
    -H 'Referer: http://statistici.insse.ro:8077/tempo-online/' \
    -H 'Sec-GPC: 1' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' \
    --data-raw '{"language":"ro","encQuery":"26958,26959:26971,26973,26974,26975,26976,26978,26979,26980:4456,4475,4779,4798,4817,4836:9685","matCode":"SAN110C","matMaxDim":4,"matUMSpec":0,"matRegJ":0}' \
    --compressed \
    --insecure >> SAN110C-data.json


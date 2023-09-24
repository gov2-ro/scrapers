see [dev notes](https://docs.google.com/document/d/1FY_1Bb2RF8JGoplnBvvIBTN-PkCfYnGR) / gDoc


- 1fetch-context.py →  context.csv

- 2fetch-dataset-list.py → datasets.csv
loops context.csv and fetches dataset lists

- 3fetch-meta → data/meta/<datasetId>.json

- 4fetch-csvs - downloads csvs

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


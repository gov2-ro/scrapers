scrape [monitoruloficial.ro/e-monitor](https://monitoruloficial.ro/e-monitor/) → save pdfs →  get text → make nice / explorable.

## Roadmap

- [x] local cache
    - [x] fetch daily părți
    - [x] download pdfs
    - [x] fetch P-III - P-VII (online for 10 days)
        - [x] fetch individual pages
        - [x] fetch jsonp's
        - [ ] concatenate pdfs
            - [ ] OCR needed pages

- [ ] structured text/html from PDF
    - [ ] PDF → HTML see [pdf2txt.xslx](https://docs.google.com/spreadsheets/d/1APEmulzWa7PGgDg_mc-7rnY_vbxX2Q6Y) 
    - [ ] split into chapters → initial UI 
    - [ ] NLP, detect entities
- [ ] UI 
- [ ] updater cron
- [ ] notifications
- [ ] annotations, relative links


## Scripts

- `get_index.py` - gets daily părți for a date range (save to sqlite or/and files)
- `fetch_pdfs.py` - reads list from sqlite, downloads pdfs
- `fetch_pdfs_p3+` - gets P.III - P.VII (ephemeral, online for 10 days)

see also [pdf2text](../pdf2text) conversion tests

## Proiecte similare

[monitoruljuridic.ro](http://www.monitoruljuridic.ro/) | [lege-online.ro/monitoare-oficiale](https://www.lege-online.ro/monitoare-oficiale) | [lege5.ro/App/MonitorOficial](https://lege5.ro/App/MonitorOficial) | [ro-lex.ro](https://www.ro-lex.ro/)    


| proiect | obs | price |
|-----|-----|-----|
| [monitoruljuridic.ro](http://www.monitoruljuridic.ro/) | no formatting | gratis |
| [lege-online.ro](https://www.lege-online.ro/monitoare-oficiale) |  |  |
| [lege5.ro](https://lege5.ro/App/MonitorOficial) | formatted, linked | paid |
| [idrept.ro](https://lege5.ro/App/MonitorOficial) | formatted, linked | paid |

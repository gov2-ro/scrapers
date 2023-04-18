scrape [monitoruloficial.ro/e-monitor](https://monitoruloficial.ro/e-monitor/) → save pdfs →  get text → analyze?.

- [x] fetch daily părți
- [x] download pdfs
- [ ] structured text/html from PDF
- [ ] updater cron

- `get_index.py` - gets daily părți for a date range (save to sqlite or/and files)
- `fetch_pdfs.py` - reads list from sqlite, downloads pdfs
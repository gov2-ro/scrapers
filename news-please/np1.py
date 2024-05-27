from newsplease import NewsPlease
url = 'https://www.adr.gov.ro/adr-anunta-rezultatele-etapei-de-verificare-a-conformitatii-administrative-a-celor-26-de-dosare-depuse-in-cadrul-procedurii-de-selectie-a-partenerilor-din-proiectul-competente-in-tehnologii-a/'
url = 'https://copii.gov.ro/1/a-n-u-n-t-privind-ocuparea-prin-transfer-la-cerere-a-unor-functii-publice-vacante-in-cadrul-autoritatii-nationale-pentru-protectia-drepturilor-copilului-si-adoptie/'
article = NewsPlease.from_url(url)
print(article.title)
print(article.language)
print(article.date_modify)
print(article.maintext)
 
import newspaper

# zi_paper = newspaper.build('http://dordeduca.ro')
# zi_paper = newspaper.build('https://ana.gov.ro/')
# zi_paper = newspaper.build('https://sgg.gov.ro/1/')
# zi_paper = newspaper.build('https://www.mcid.gov.ro/')
zi_paper = newspaper.build('https://anes.gov.ro/')
print('-- articles')

ii = 0

for article in zi_paper.articles:
    print(article.url)
    ii = ii + 1
    if ii >=14:
        break

print('-- categories')
ii = 0
 
for category in zi_paper.category_urls():
    print(category)
    ii = ii + 1
    if ii >=14:
        break

print('--done')
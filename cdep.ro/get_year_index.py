import csv, sqlite3 
base = 'https://www.cdep.ro/pls/proiecte/upl_pck2015.lista?cam=2'
output_csv = '../data/cdep/liste-legi-ani-cdep.csv'
db_filename = '../data/cdep/cdep.db'
table = 'src_years'

def incremental_urls(preffix = '', suffix = '', min_val = 1996, max_val = 2023):
    # Initialize the counter to the minimum value
    counter = min_val
    # Convert the counter to a string of the same length as the maximum value
    counter_str_format = '{:0' + str(len(str(max_val))) + 'd}'
    # Generate the list of strings with incremental numbers
    strings = [preffix + counter_str_format.format(counter) + suffix for counter in range(min_val, max_val+1)]
    # Return the list of strings
    return strings

def build_list(ctg, preffix = '', suffix = '', min_val = 1996, max_val = 2023):
    ii = min_val
    zething = []
    for ii in range (min_val, max_val):
        ll={
            'id':ctg + str(ii),
            'ctg': ctg,
            'val': ii,
            'url': preffix  + str(ii) + suffix
        }
        zething.append(ll)
    return zething

anp_inregistrate = build_list('anp', base + '&anp=','',1996, 2023)
anb_neprocesate = build_list('anb', base + '&anb=','',1996, 2023)
anl_promulgate = build_list('anl', base + '&anl=','',1996, 2023)
ans_respinse = build_list('ans', base + '&std=O&ans=','',1996, 2023)

zidata = anp_inregistrate + anb_neprocesate + anl_promulgate + ans_respinse 

 
# Open the file in write mode
with open(output_csv, 'w', newline='') as csvfile:
    # Define the field names based on the keys in the dictionary
    fieldnames = zidata[0].keys()

    # Create a CSV writer object and write the header row
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Write the zidata rows
    for row in zidata:
        writer.writerow(row)

print(f'Output written to {output_csv}')

conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS ''' + table + '''
             (id TEXT, ctg TEXT, val INTEGER, url TEXT)''')

for row in zidata:
    c.execute("INSERT INTO " + table + " (id, ctg, val, url) VALUES (?, ?, ?, ?)", (row['id'], row['ctg'], row['val'], row['url']))


conn.commit()
conn.close()

print(f'Data written to {db_filename}')
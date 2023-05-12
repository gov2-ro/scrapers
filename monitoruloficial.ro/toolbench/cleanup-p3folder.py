""" moves mo folders in root under respective dates """

import os, sqlite3, sys, shutil, logging

root_folder =   '../../data/mo/pdfs/_p3+/tmp/'
db_filename     =   '../../data/mo/mo.db'
table_name      =   'dates_lists'


conn = sqlite3.connect(db_filename)
c = conn.cursor()

for mofolder in os.listdir(root_folder):
    # check if foldername is in db and move it to folder 
    qq = "SELECT * from '" + table_name + "' WHERE json LIKE  '%" + mofolder + "%';"
    c.execute(qq) 
    rows = c.fetchall()
    nrows = len(rows)
 
    if nrows >> 1:
        print ('Err19: ' + str(nrows) + ' rows!')
        print (qq)
        sys.exit()
    if nrows == 0:
        continue
 
    zidate = rows[0][0]
    print(zidate)
    if not os.path.isdir(root_folder + zidate ):
        os.makedirs(root_folder + zidate)
       
    try:
        shutil.move(root_folder + mofolder, root_folder + zidate )
    except Exception as e:
            print(' mv ' + root_folder + mofolder + ' --> ' + root_folder + zidate)
            logging.error(f'ERR34: mv {root_folder + zidate }: {e}')
    print (mofolder)

print ('done')



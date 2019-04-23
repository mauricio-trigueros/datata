import os
from shlex import quote
from datetime import datetime

def full_backup(settings):
    print ("  Full database backup")
    timeNow = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # The path can contain spaces, so we escape them with "quote"
    backupFileIso = quote("{}/mysql_full_backup_{}.sql".format(settings['local'],timeNow))
    #print (settings)
    dumpDbCommand = "mysqldump --single-transaction --user={} --password={} --host={} --port={} {} > {}".format(
        settings['mysql-user'],
        settings['mysql-pass'],
        settings['mysql-host'],
        settings['mysql-port'],
        settings['mysql-db'],
        backupFileIso)
    print ("  Dumping database....")
    os.system(dumpDbCommand)
    print ("  Done!!")

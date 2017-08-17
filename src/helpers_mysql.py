from datetime import datetime
import os

def command_full_backup(settings):
	print "  Full database backup"
	timeNow = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	backupFileIso = "{}/mysql_full_backup_{}.sql".format(settings['local'],timeNow)
	print (settings)
	dumpDbCommand = "mysqldump --single-transaction --user={} --password={} --host={} --port={} {} > {}".format(
		settings['mysql-user'],
		settings['mysql-pass'],
		settings['mysql-host'],
		settings['mysql-port'],
		settings['mysql-db'],
		backupFileIso)
	print "  Executing command '{}'".format(dumpDbCommand)
	os.system(dumpDbCommand)

# All helpers have an iterator.
# In this case our database iterator is not iterating, 
# just calling the callback function.
# TODO may be iterate table by table?
def iterator(settings, function_callback):
	print "Mysql start iterating "
	function_callback(settings)
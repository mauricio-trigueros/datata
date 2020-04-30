import os
from shlex import quote
from datetime import datetime
from lib.commands_local import LocalFile

class MysqlClient:

	def __init__(self, host, port, user, pwd, db):
		self.host = host
		self.port = port
		self.user = user
		self.pwd = pwd
		self.db = db

	# Creates the dump file that we will use to keep the dump file
	def create_dump_file(self, folder) -> LocalFile:
		#time_now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		time_now = '2020-04-18_18-11-24'
		# The path can contain spaces, so we escape them with "quote"
		dump_file = LocalFile(os.path.normpath(quote("{}/mysql_full_backup_{}.sql".format(folder, time_now))))
		print("  Mysql dump: {}".format(dump_file.path))
		return dump_file

	# Takes as parameter the folder where we will keep the database dump.
	def dump_database(self, folder) -> LocalFile:
		print("Dumping database")
		dump_file = self.create_dump_file(folder)
		return dump_file
		dump_db = "mysqldump --single-transaction --user={user} --password={pwd} --host={host} --port={port} {db} > {file}".format(
			user=self.user,
			pwd=self.pwd,
			host=self.host,
			port=self.port,
			db=self.db,
			file=dump_file.path
		)
		print ("  Dumping database....")
		os.system(dump_db)
		dump_file.is_valid_or_die()
		print ("  Done!!")
		return dump_file
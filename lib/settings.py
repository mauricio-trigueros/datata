import sys
import getopt

from lib.commands_s3 import S3
from lib.commands_server import Server
from lib.commands_local import Local
from lib.commands_mysql import Mysql

ACTIONS = {}

ACTIONS['download_from_server_to_local'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
	'description': 'Downloading content from server to local...'
}
ACTIONS['upload_from_local_to_server'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
	'description': 'Uploading files from local to server...'
}
ACTIONS['compress_local_images'] = {
	'mandatory_values': ['local-folder', 'local-dest', 'force', 'dry-run'],
	'description': 'Compressing local images...'
}
ACTIONS['s3_upload'] = {
	'mandatory_values': ['s3-key', 's3-secret', 's3-bucket', 's3-prefix', 's3-storage', 'dry-run'],
	'description': 'Uploading files to S3...'
}
ACTIONS['s3_download'] = {
	'mandatory_values': ['s3-key', 's3-secret', 's3-bucket', 's3-prefix', 's3-storage', 'dry-run'],
	'description': 'Downloading files from S3...'
}
ACTIONS['backup_database'] = {
	'mandatory_values': ['local-folder', 'mysql-host', 'mysql-port', 'mysql-user', 'mysql-pass', 'mysql-db'],
	'description': 'Backing up database...'
}
ACTIONS['mirror_server_to_local'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
	'description': 'Mirroring server to local...'
}
ACTIONS['mirror_local_to_server'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
	'description': 'Mirroring local to server...'
}
ACTIONS['mirror_local_folders_by_name'] = {
	'mandatory_values': ['local-folder', 'local-dest', 'dry-run'],
	'description': 'Mirroring local folders by name...'
}
ALLOWED_PARAMETERS = [
	"action",    # Name of the command we want to execute (from commands.py)
	"dry-run",    # Boolean, to indicate if we must execute command or just dry-run

	"serv-url",   # Server IP, like "192.168.100.90"
	"serv-user",  # User to login into the server
	"serv-key",   # Path to the SSH key to connect to the server
	"serv-folder", # Folder inside the server, like "/var/www/myproject/"

	"s3-key",		# AWS IAM Key to handle the bucket
	"s3-secret",	# AWS IAM Secret to handle the bucket
	"s3-bucket",	# AWS S3 bucket name
	"s3-prefix",	# AWS S3 prefix (subfolder inside the folder where we will work)
	"s3-storage",	# AWS S3 storage to use for uploads ('STANDARD', 'REDUCED_REDUNDANCY', 'STANDARD_IA')
	"s3-acl",		# AWS S3 ACL to set for uploads

	"mysql-host",
	"mysql-port",
	"mysql-user",
	"mysql-pass",
	"mysql-db",

	"force", # Force to run action, like compress again an existing picture

	"local-folder",      # Local full path, it needs to exist
	"local-dest",
]

def settings():
	try:
		opts, args = getopt.getopt(
			sys.argv[1:],
			':'.join(ALLOWED_PARAMETERS)+':', # Convert to "command:key:secret:bucket:prefix:..."
			[param+"=" for param in ALLOWED_PARAMETERS] # Convert to ['command=', 'key=', 'secret=', ...]
		)
	except getopt.GetoptError as e:
		print ("Wrong parameters: {}".format(e))
		print ("Allowed parameters are: {}".format(', '.join(ALLOWED_PARAMETERS)))
		sys.exit(2)

	# Start parsing values and adding them to settings object:
	raw_settings = {}
	for opt, arg in opts:
		# Validate opt to see if matches ALLOWED_PARAMETERS.
		# We expect all parameters like: --command="list_s3_files" --key="PAPAPA01234567"
		if opt[2:] in ALLOWED_PARAMETERS:
			raw_settings[opt[2:]] = arg

	action = ACTIONS.get(raw_settings['action'], False)
	if not action:
		sys.exit("Unknown or wrong parameter --action '{}'".format(raw_settings['action']))

	# Verify that action has mandatory values
	for field in action.get('mandatory_values'):
		print ("  Validating field '{}'... ".format(field), end='')
		if field in raw_settings:
			print ("present: {}".format(raw_settings[field]))
		else:
			print ("missing!!")
			sys.exit("Mandatory field '{}' not found".format(field))

	raw_settings['description'] = action.get('description')

	return parse_settings(raw_settings)

def parse_settings(raw_settings):
	# Parsing settings
	settings = {}

	# Action is always mandatory
	settings['action'] = raw_settings['action']
	settings['description'] = raw_settings['description']

	# Dry run is not mandatory (for example, to list a bucket content)
	settings['dry-run'] = False if raw_settings.get('dry-run', 'True').lower() in ("no", "false", False) else True
	settings['force'] = False if raw_settings.get('force', 'False').lower() in ("no", "false") else True
	# if "dry-run" in raw_settings:
	# 	settings['dry-run'] = False if raw_settings.get('dry-run').lower() in ("no", "false", False) else True
	# if "force" in raw_settings:
	# 	settings['force'] = False if raw_settings['force'].lower() in ("no", "false") else True

	# Local settings
	if set(('local-folder',)).issubset(raw_settings):
		local = Local(
			dry_run=settings['dry-run'],
			force=settings['force'],
			local_folder=raw_settings['local-folder'],
			dest_folder=raw_settings.get('local-dest', False)
		)
		settings['local'] = local

	# S3 settings
	if set(('s3-bucket','s3-key','s3-secret')).issubset(raw_settings):
		print("Creating S3..")
		s3_class = S3(
			settings['dry-run'],
			raw_settings['s3-bucket'],
			raw_settings['s3-key'],
			raw_settings['s3-secret'],
			raw_settings['s3-prefix'],
			raw_settings['s3-storage'],
			raw_settings['s3-acl']
		)
		settings['s3'] = s3_class

	# Create SSH client (if need it)
	if set(("serv-url","serv-user","serv-key")).issubset(raw_settings):
		ssh_client = Server(
			settings['dry-run'],
			raw_settings['serv-url'], 
			raw_settings['serv-user'], 
			raw_settings['serv-key'],
			raw_settings['serv-folder']
		)
		settings['server'] = ssh_client

	# MySQL settings
	if set(("mysql-host","mysql-port","mysql-user","mysql-pass","mysql-db")).issubset(raw_settings):
		mysql_client = Mysql(
			raw_settings['mysql-host'],
			raw_settings['mysql-port'],
			raw_settings['mysql-user'],
			raw_settings['mysql-pass'],
			raw_settings['mysql-db'],
		)
		settings['mysql'] = mysql_client
	
	return settings

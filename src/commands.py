import sys

command = {}

command['download_files_from_s3'] = {
	'command': 'helpers_s3.command_download_files',
	'mandatory_values': ['secret','key','bucket','local','dry-run'],
	'iterator': 'helpers_s3.iterator',
	'example': 'python run.py --command="download_files_from_s3" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --dry-run="True"',
	'description': 'Download the "bucket" content (from "prefix") to "local" path, if "dry-run" is False. Otherwise just list the files that are going to be downloaded.'
}

command['upload_files_to_s3'] = {
	'command': 'helpers_s3.command_upload_files',
	'mandatory_values': ['secret','key','bucket','local','dry-run'],
	'iterator': 'helpers_local.iterator',
	'example': 'python run.py --command="upload_files_to_s3" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --dry-run="True"',
	'description': 'Upload "prefix" folder inside "local" folder, to "bucket", with the same "prefix"; if "dry-run" is False. Otherwise just list the files that are going to be uploaded.'
}

command['list_s3_files'] = {
	'command': 'helpers_s3.command_list_bucket_content',
	'mandatory_values': ['secret','key','bucket'],
	'iterator': 'helpers_s3.iterator',
	'example': 'python run.py --command="list_s3_files" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/"',
	'description': 'List the content of the "bucket", starting from the "prefix".'
}

command['set_s3_cache_control'] = {
	'command': 'helpers_s3.command_set_cache_control',
	'mandatory_values': ['secret','key','bucket','dry-run'],
	'iterator': 'helpers_s3.iterator',
	'example': 'python run.py --command="set_s3_cache_control" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"',
	'description': 'Set the Cache-Control header, for "bucket" (with "prefix"). Cache-Control is set in "helpers_files.py", method "get_cache_control_per_extension". If "dry-run" is True, files will not be affected, just listed.'
}

command['set_s3_file_mime_type'] = {
	'command': 'helpers_s3.command_set_file_mime_type',
	'mandatory_values': ['secret','key','bucket','dry-run'],
	'iterator': 'helpers_s3.iterator',
	'example': 'python run.py --command="set_s3_file_mime_type" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"',
	'description': 'Add mime type to files in "bucket" (with "prefix"), based on file extension. List is in method "get_content_type_per_extension", in "helpers_files.py". Only files are changed if "dry-run" is False.'
}

command['list_local_folder'] = {
	'command': 'helpers_local.command_list_folder_content',
	'mandatory_values': ['local'],
	'iterator': 'helpers_local.iterator',
	'example': 'python run.py --command="list_local_folder" --local="/Users/me/folder"',
	'description': 'List the folder content of "local" path.'
}

# TODO: check if result already exist in "hash-file", and update it, instead of appending it to the end?
command['calculate_hash'] = {
	'command': 'helpers_local.command_calculate_hash',
	'mandatory_values': ['local','hash-file'],
	'iterator': 'helpers_local.iterator',
	'example': 'python run.py --command="calculate_hash" --local="/Users/me/folder" --hash-file="/Users/me/Downloads/hash.txt"',
	'description': 'Calculate hash for local files "local", and leave the result in "hash-file". This "hash-file" needs to exist, and hashes will be appended to the end of file.'
}

command['verify_hash'] = {
	'command': 'helpers_local.command_verify_hash',
	'mandatory_values': ['local','hash-file'],
	'iterator': 'helpers_local.iterator',
	'example': 'python run.py --command="verify_hash" --local="/Users/me/folder" --hash-file="/Users/me/Downloads/hash.txt"',
	'description': 'Validate if hash calculated with command "calculate_hash" matches the files.' 
}

command['list_server_folder'] = {
	'command': 'helpers_server.command_list_folder_content',
	'mandatory_values': ['serv-url','serv-user','serv-pass','serv-folder', 'serv-key'],
	'iterator': 'helpers_server.iterator',
	'example': 'python run.py --command="list_server_folder" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"',
	'description': 'List the server remote folder "serv-folder". It uses a ssh key "serv-key" or a server password "serv-pass" to connect to the server. If you want to use a password, then set "serv-key" to "/dev/null". If you want to use a SSH key, then set "serv-pass" to "".'
}

command['download_files_from_server'] = {
	'command': 'helpers_server.command_download_files',
	'mandatory_values': ['serv-url','serv-user','serv-pass','serv-key','serv-folder', 'local','dry-run'],
	'iterator': 'helpers_server.iterator',
	'example': 'python run.py --command="download_files_from_server" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"  --local="/Users/me/folder" --dry-run="False"',
	'description': 'Download the files in remote server "serv-folder" to local folder "local" (if "dry-run" is False). It uses a ssh key "serv-key" or a server password "serv-pass" to connect to the server. If you want to use a password, then set "serv-key" to "/dev/null". If you want to use a SSH key, then set "serv-pass" to "".'
}

command['mysql_full_backup'] = {
	'command': 'helpers_mysql.command_full_backup',
	'mandatory_values': ['local','mysql-host','mysql-port','mysql-user','mysql-pass', 'mysql-db'],
	'iterator': 'helpers.null_iterator',
	'example': 'python run.py --command="mysql_full_backup" --local="/Users/me/folder" --mysql-host="192.168.100.72" --mysql-port="3306" --mysql-user="dev-user" --mysql-pass="dev-pass" --mysql-db="mydb"',
	'description': 'Perform a full MySQL database dump to folder "local", with SQL file name "mysql_full_backup_DATE.sql".'
}

command['list_commands'] = {
	'command': 'helpers.command_list_commands',
	'mandatory_values': [],
	'iterator': 'helpers.null_iterator',
	'example': 'python run.py --command="list_commands"',
	'description': 'List all the commands supported by the program'
}

def get_command_or_die(command_name):
	if command_name in command:
		return command[command_name]
	else:
		sys.exit("Command name '{}' not found".format(command_name))

def validate_command_values_or_die(command_object, raw_settings):
	for field in raw_settings['command']['mandatory_values']:
		print "Validating field '{}'... ".format(field),
		if field in raw_settings:
			print "present!"
		else:
			print "missing!!"
			sys.exit("Mandatory field '{}' not found".format(field))

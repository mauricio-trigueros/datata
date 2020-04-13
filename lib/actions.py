import sys
import getopt

from lib.helpers import create_ssh_client_or_die
from lib.commands_local import validate_local_folder_or_die

ACTIONS = {}

ACTIONS['download_from_server_to_local'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
}
ACTIONS['upload_from_local_to_server'] = {
	'mandatory_values': ['serv-url','serv-user','serv-key','serv-folder', 'local-folder','dry-run'],
}
ACTIONS['compress_local_images'] = {
	'mandatory_values': ['local-folder', 'local-dest', 'force', 'dry-run'],
}
ALLOWED_PARAMETERS = [
	"action",    # Name of the command we want to execute (from commands.py)
	"dry-run",    # Boolean, to indicate if we must execute command or just dry-run

	"serv-url",   # Server IP, like "192.168.100.90"
	"serv-user",  # User to login into the server
	"serv-key",   # Path to the SSH key to connect to the server
	"serv-folder", # Folder inside the server, like "/var/www/myproject/"

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
		print ("Mandatory parameter is '--command'")
		print ("Allowed parameters are: {}".format(', '.join(ALLOWED_PARAMETERS)))
		sys.exit(2)

	# Start parsing values and adding them to settings object:
	raw_settings = {}
	for opt, arg in opts:
		# Validate opt to see if matches ALLOWED_PARAMETERS.
		# We expect all parameters like: --command="list_s3_files" --key="PAPAPA01234567"
		if opt[2:] in ALLOWED_PARAMETERS:
			raw_settings[opt[2:]] = arg

	# Value command is mandatory!!
	if (not 'action' in raw_settings):
		sys.exit("Mandatory fields: action")

	# Get action dictionary object
	action = ACTIONS.get(raw_settings['action'])

	# Verify that action has mandatory values
	for field in action.get('mandatory_values'):
		print ("Validating field '{}'... ".format(field), end='')
		if field in raw_settings:
			print ("present!")
		else:
			print ("missing!!")
			sys.exit("Mandatory field '{}' not found".format(field))

	return parse_settings(raw_settings)

def parse_settings(raw_settings):
	# Parsing settings
	settings = {}
	settings['action'] = raw_settings['action']

	if "serv-folder" in raw_settings:
		settings['serv-folder'] = raw_settings['serv-folder']

	settings['local-folder'] = validate_local_folder_or_die(raw_settings['local-folder'])
	if "local-dest" in raw_settings:
		settings['local-dest'] = validate_local_folder_or_die(raw_settings['local-dest'])

	# Dry run is not mandatory (for example, to list a bucket content)
	if "dry-run" in raw_settings:
		settings['dry-run'] = False if raw_settings['dry-run'].lower() in ("no", "false") else True

	if "force" in raw_settings:
		settings['force'] = False if raw_settings['force'].lower() in ("no", "false") else True

	# Create SSH client (if need it)
	if set(("serv-url","serv-user","serv-key")).issubset(raw_settings):
		print ("Creating SSH client...")
		ssh_client = create_ssh_client_or_die(
			server=raw_settings['serv-url'], 
			username=raw_settings['serv-user'], 
			password='',
			key=raw_settings['serv-key']
		)
		settings['server_client'] = ssh_client

	return settings

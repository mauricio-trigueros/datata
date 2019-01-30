import sys
import getopt
import tempfile

from src.server.helpers import create_ssh_client_or_die
from src.s3.helpers import create_s3_client_or_die
from src.local.file import validate_local_folder_or_die, verify_and_create_local_folder_path

from src.mimes import is_jpg, is_png, is_video

from src.s3.helpers import get_bucket_inventory

from . import commands


ALLOWED_PARAMETERS = [
    "command",    # Name of the command we want to execute (from commands.py)
    "key",        # AWS IAM key for connecting to the S3 bucket
    "secret",     # AWS IAM secret for connecting to the S3 bucket
    "bucket",     # AWS Bucket name
    "prefix",     # Prefix to start iterating from an S3 bucket, ending with "/", like "assets/images/"
    "local",      # Local full path, it needs to exist
    "local-dest", # Locall full path for destination, it needs to exist
    "dry-run",    # Boolean, to indicate if we must execute command or just dry-run
    "delete-after",     # Delete after
    "hash-file",  # Path to the file containing hashes, like "/Users/me/Downloads/hash.txt"
    "strategy",
    "serv-url",   # Server IP, like "192.168.100.90"
    "serv-user",  # User to login into the server
    "serv-pass",  # If we want to use SSH password (instead of SSH key)
    "serv-key",   # Path to the SSH key to connect to the server
    "serv-folder", # Folder inside the server, like "/var/www/myproject/"
    "s3-prefix", 
    "s3-storage",
    "mysql-host",     # MYSQL server url
    "mysql-port",     # MYSQL server port
    "mysql-user",     # MYSQL server username
    "mysql-pass",     # MYSQL server password
    "mysql-db"        # MYSQL 
]

def parse_raw_settings(raw_settings):

    settings = {}
    settings['command'] = raw_settings['command']
    settings['prefix'] = raw_settings['prefix'] if 'prefix' in raw_settings else ''

    if set(("secret","key","bucket")).issubset(raw_settings):
        # Setting S3 bucket
        settings['s3_client'] = create_s3_client_or_die(raw_settings['key'],raw_settings['bucket'],raw_settings['secret'])
        settings['s3_bucket'] = raw_settings['bucket']

    # Dry run is not mandatory (for example, to list a bucket content)
    if "dry-run" in raw_settings:
        settings['dry-run'] = False if raw_settings['dry-run'].lower() in ("no", "false") else True

    if "delete-after" in raw_settings:
        settings['delete-after'] = False if raw_settings['delete-after'].lower() in ("no", "false") else True

    if "local" in raw_settings:
        # local will depend on kind of command to run:
        # If we run a "list" command we should not create anything
        if settings['command']['command'] in ['list', 'local_commands.print_path'] :
            # List command, do not create anything!
            settings['local'] = validate_local_folder_or_die(raw_settings['local'])
        else:
            settings['local'] = verify_and_create_local_folder_path(raw_settings['local'])

    if "local-dest" in raw_settings:
        settings['local-dest'] = verify_and_create_local_folder_path(raw_settings['local-dest'])

    if "hash-file" in raw_settings:
        settings['hash-file'] = validate_local_folder_or_die(raw_settings['hash-file'])

    if "strategy" in raw_settings:
        settings['strategy'] = raw_settings['strategy']

    if "s3-prefix" in raw_settings:
        settings['s3-prefix'] = raw_settings['s3-prefix']

    if "s3-storage" in raw_settings:
        # We plug this value directly in boto (http://boto3.readthedocs.io/en/latest/reference/services/s3.html)
        if raw_settings['s3-storage'] in ['STANDARD', 'REDUCED_REDUNDANCY', 'STANDARD_IA']:
            settings['s3-storage'] = raw_settings['s3-storage']
        else:
            sys.exit("Parameter s3-storage '{}' not valid, valids are 'STANDARD', 'REDUCED_REDUNDANCY', 'STANDARD_IA'".format(raw_settings['s3-storage']))

    settings['serv-folder'] = raw_settings['serv-folder'] if 'serv-folder' in raw_settings else ''
    if set(("serv-url","serv-user","serv-pass","serv-folder")).issubset(raw_settings):
        print ("Creating SSH client...")
        #print (raw_settings)
        ssh_client = create_ssh_client_or_die(
            server=raw_settings['serv-url'], 
            username=raw_settings['serv-user'], 
            password=raw_settings['serv-pass'],
            key=raw_settings['serv-key']
        )
        settings['server_client'] = ssh_client

    # Adding temporal folders
    settings["temp_folder_1"] = tempfile.mkdtemp()
    settings["temp_folder_2"] = tempfile.mkdtemp()

    # Adding mysql parameters:
    settings["mysql-user"] = raw_settings['mysql-user'] if "mysql-user" in raw_settings else False
    settings["mysql-pass"] = raw_settings['mysql-pass'] if "mysql-pass" in raw_settings else False
    settings["mysql-host"] = raw_settings['mysql-host'] if "mysql-host" in raw_settings else False
    settings["mysql-port"] = raw_settings['mysql-port'] if "mysql-port" in raw_settings else False
    settings["mysql-db"] = raw_settings['mysql-db'] if "mysql-db" in raw_settings else False

    if settings['command']['s3_inventory']:
        print ("Getting S3 inventory....")
        settings['s3_inventory'] = get_bucket_inventory(settings)

    return settings

# Read raw settings.
# Parameter dest is the destination: s3, local (or server, etc etc)
# Depending on dest, we will set some parameters as mandatory.
# Target needs to be like: "/Users/me/DELETEME/testsync/", starting and ending with "/"
def read_raw_settings():
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
    if (not 'command' in raw_settings):
        sys.exit("Mandatory fields: command")

    # If command is valid, get command object
    raw_settings['command'] = commands.get_command_or_die(raw_settings['command'])
    # Validate that all 
    commands.validate_command_values_or_die(raw_settings['command'], raw_settings)

    return raw_settings

def null_iterator(settings, function_callback):
    function_callback(settings)

def command_list_commands(settings):
    print ("LISTING COMMANDS")
    for name, data in commands.command.items():
        print ("\n  Command: {}".format(name))
        print ("    {}".format(data.get('description', '(no description provided)')))
        print ("    Mandatory values: {}".format(data['mandatory_values']))
        print ("    Example: {}".format(data.get('example', '(no example provided)')))

# Return the command to execute when compressing pictures.
# Path parameters needs to be full paths.
# If original_full_path is not a picture, then returns false.
def get_image_comp_command(original_full_path, comp_full_path):
    # Compressing file
    if is_jpg(original_full_path):
        return "jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(original_full_path, comp_full_path)
    elif is_png(original_full_path):
        return "pngquant --force --skip-if-larger --quality 40-90 --speed 1 --output '{}' '{}'".format(comp_full_path, original_full_path)
    else:
        return False

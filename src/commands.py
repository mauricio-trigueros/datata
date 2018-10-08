import sys

command = {}

##
# Server commands
#
command['server_list_folders'] = {
    'command': 'server_commands.print_path',
    'mandatory_values': ['serv-url', 'serv-user', 'serv-pass', 'serv-key', 'serv-folder'],
    'iterator': 'server_iterators.folders',
    'example': 'python datata.py --command="server_list_folders" --local="/Users/me/Deleteme/files/"',
    'description': 'List all folders for given path'
}
command['server_list_files'] = {
    'command': 'server_commands.print_path',
    'mandatory_values': ['serv-url','serv-user','serv-pass','serv-folder', 'serv-key'],
    'iterator': 'server_iterators.files',
    'example': 'python datata.py --command="server_list_files" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"',
    'description': 'List all files for a given path'
}
command['server_folders_info'] = {
    'command': 'server_commands.folders_info',
    'mandatory_values': ['serv-url', 'serv-user', 'serv-pass', 'serv-key', 'serv-folder'],
    'iterator': 'server_iterators.folders',
    'example': 'python datata.py --command="server_folders_info" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"',
    'description': 'List all folders for given path, plus extra information'
}
command['server_files_info'] = {
    'command': 'server_commands.files_info',
    'mandatory_values': ['serv-url', 'serv-user', 'serv-pass', 'serv-key', 'serv-folder'],
    'iterator': 'server_iterators.files',
    'example': 'python datata.py --command="server_files_info" --local="/Users/me/Deleteme/files/"',
    'description': 'List all files for a given path, plus extra information'
}
command['server_download'] = {
    'command': 'server_commands.download_files',
    'mandatory_values': ['serv-url','serv-user','serv-pass','serv-key','serv-folder', 'local','dry-run'],
    'iterator': 'server_iterators.fast_files',
    'example': 'python datata.py --command="server_download" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"  --local="/Users/me/folder/" --dry-run="False"',
    'description': 'Download the files in remote server "serv-folder" to local folder "local" (if "dry-run" is False). It uses a ssh key "serv-key" or a server password "serv-pass" to connect to the server. If you want to use a password, then set "serv-key" to "/dev/null". If you want to use a SSH key, then set "serv-pass" to "".'
}
command['remote_compress_images'] = {
    'command': 'server_commands.remote_compress_images',
    'mandatory_values': ['serv-url','serv-user','serv-pass','serv-key','serv-folder','dry-run'],
    'iterator': 'server_iterators.files',
    'example': 'python datata.py --command="remote_compress_images" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/" --dry-run="False"',
    'description': 'Compress remote images, it downloaded them, then compress them in local, and uplad them again.'
}

##
# Local commands
#
command['local_list_folders'] = {
    'command': 'local_commands.print_path',
    'mandatory_values': ['local'],
    'iterator': 'local_iterators.folders',
    'example': 'python datata.py --command="local_list_folders" --local="/Users/me/folder/"',
    'description': 'List the folder content of "local" path.'
}
command['local_list_files'] = {
    'command': 'local_commands.print_path',
    'mandatory_values': ['local'],
    'iterator': 'local_iterators.files',
    'example': 'python datata.py --command="local_list_files" --local="/Users/me/folder/"',
    'description': 'List the folder content of "local" path.'
}
command['local_folders_info'] = {
    'command': 'local_commands.folders_info',
    'mandatory_values': ['local'],
    'iterator': 'local_iterators.folders',
    'example': 'python datata.py --command="local_folders_info" --local="/Users/me/Deleteme/files/"',
    'description': 'List all folders for given path, plus extra information'
}
command['local_files_info'] = {
    'command': 'local_commands.files_info',
    'mandatory_values': ['local'],
    'iterator': 'local_iterators.files',
    'example': 'python datata.py --command="local_files_info" --local="/Users/me/Deleteme/files/"',
    'description': 'List all files for a given path, plus extra information'
}
command['compress_images'] = {
    'command': 'local_commands.compress_images',
    'mandatory_values': ['local', 'local-dest', 'strategy', 'delete-after'],
    'iterator': 'local_iterators.images',
    'example': 'python datata.py --command="compress_images" --local="/Users/me/Deleteme/files/" --local-dest="/Users/me/Deleteme/parsed/" --strategy="skip-if-exist" --delete-after="false"',
    'description': 'Compress pictures. If you want to overwrite, select overwrite strategy, otherwise skip-if-exist'
}
command['tar_files'] = {
    'command': 'local_commands.tar_files',
    'mandatory_values': ['local', 'local-dest', 'strategy', 'delete-after'],
    'iterator': 'local_iterators.files',
    'example': 'python datata.py --command="tar_files" --local="/Users/me/Deleteme/files/" --local-dest="/Users/me/Deleteme/parsed/" --strategy="skip-if-exist" --delete-after="false"',
    'description': 'Compress files. If you want to overwrite, select overwrite strategy, otherwise skip-if-exist'
}
command['verify_videos'] = {
    'command': 'local_commands.verify_videos',
    'mandatory_values': ['local'],
    'iterator': 'local_iterators.files',
    'example': 'python datata.py --command="verify_videos" --local="/Users/me/Deleteme/VIDEOS/"',
    'description': 'Verify (recursively) videos for a given folder. For each video found, it prints the video status.'
}

##
# S3 commands
#
command['s3_list_files'] = {
    'command': 's3_commands.print_path',
    'mandatory_values': ['secret','key','bucket'],
    'iterator': 's3_iterators.iterator',
    'example': 'python datata.py --command="s3_list_files" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/"',
    'description': 'List the content of the "bucket", starting from the "prefix".'
}
command['s3_download'] = {
    'command': 's3_commands.download_files',
    'mandatory_values': ['secret','key','bucket','local','dry-run'],
    'iterator': 's3_iterators.iterator',
    'example': 'python datata.py --command="s3_download" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --dry-run="True"',
    'description': 'Download the "bucket" content (from "prefix") to "local" path, if "dry-run" is False. Otherwise just list the files that are going to be downloaded.'
}
command['s3_upload'] = {
    'command': 's3_commands.upload_files',
    'mandatory_values': ['secret','key','bucket','local','s3-prefix','s3-storage','dry-run'],
    'iterator': 'local_iterators.files',
    'example': 'python datata.py --command="s3_upload" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --s3-prefix="" --s3-storage="STANDARD" --dry-run="True"',
    'description': 'Upload "prefix" folder inside "local" folder, to "bucket", with the same "prefix"; if "dry-run" is False. Otherwise just list the files that are going to be uploaded.'
}
command['s3_set_cache_control'] = {
    'command': 's3_commands.set_cache_control',
    'mandatory_values': ['secret','key','bucket','dry-run'],
    'iterator': 's3_iterators.iterator',
    'example': 'python datata.py --command="s3_set_cache_control" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"',
    'description': 'Set the Cache-Control header, for "bucket" (with "prefix"). Cache-Control is set in "helpers_files.py", method "get_cache_control_per_extension". If "dry-run" is True, files will not be affected, just listed.'
}
command['s3_set_mime_type'] = {
    'command': 's3_commands.set_mime_type',
    'mandatory_values': ['secret','key','bucket','dry-run'],
    'iterator': 's3_iterators.iterator',
    'example': 'python datata.py --command="s3_set_mime_type" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"',
    'description': 'Add mime type to files in "bucket" (with "prefix"), based on file extension. List is in method "get_content_type_per_extension", in "helpers_files.py". Only files are changed if "dry-run" is False.'
}

##
# Mysql
#
command['mysql_full_backup'] = {
    'command': 'mysql_commands.full_backup',
    'mandatory_values': ['local','mysql-host','mysql-port','mysql-user','mysql-pass', 'mysql-db'],
    'iterator': 'helpers.null_iterator',
    'example': 'python datata.py --command="mysql_full_backup" --local="/Users/me/folder" --mysql-host="192.168.100.72" --mysql-port="3306" --mysql-user="dev-user" --mysql-pass="dev-pass" --mysql-db="mydb"',
    'description': 'Perform a full MySQL database dump to folder "local", with SQL file name "mysql_full_backup_DATE.sql".'
}

##
# Other commands
#
command['list_commands'] = {
    'command': 'helpers.command_list_commands',
    'mandatory_values': [],
    'iterator': 'helpers.null_iterator',
    'example': 'python datata.py --command="list_commands"',
    'description': 'List all the commands supported by the program'
}


def get_command_or_die(command_name):
    if command_name in command:
        return command[command_name]
    else:
        sys.exit("Command name '{}' not found".format(command_name))

def validate_command_values_or_die(command_object, raw_settings):
    for field in raw_settings['command']['mandatory_values']:
        print ("Validating field '{}'... ".format(field), end='')
        if field in raw_settings:
            print ("present!")
        else:
            print ("missing!!")
            sys.exit("Mandatory field '{}' not found".format(field))

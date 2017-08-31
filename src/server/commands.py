from .file import get_size
from .file import count_files_in_folder
from .file import get_file_hash
from src.comparators import local_and_server_files_are_equals
from src.local.file import verify_and_create_local_folder_path

##
# Server commands
##

# Get information about the remote folder, like size and number of items
def folders_info(settings, server_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], server_rel_path)
	folder_size = get_size(settings, full_path)
	num_files = count_files_in_folder(settings, full_path)
	print (" FOLDER '{}'   {} bytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, server_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], server_rel_path)
	file_hash = get_file_hash(settings, full_path)
	file_size = get_size(settings, full_path)
	print (" FILE '{}'   {} hash {} bytes ".format(full_path, file_hash, file_size))

def print_path(settings, server_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], server_rel_path)
	print ("        '{}'   ".format(full_path))

def download_files(settings, relative_path):
	print ("Downloading {}".format(relative_path)),
	print (" --downloading"),
	full_local_path = "{}{}".format(settings['local'],relative_path)
	full_remote_path = "{}{}".format(settings['serv-folder'],relative_path)

	# Check if files are the same!!
	if local_and_server_files_are_equals(settings, full_local_path, full_remote_path):
		print ("--untouched --DONE")
		return

	print (" --downloading..."),
	# If we are in dry mode, do nothing
	if settings['dry-run']:
		print (" --DRY-RUN")
	else:
		verify_and_create_local_folder_path(full_local_path)
		sftp = settings['server_client'].client.open_sftp()
		sftp.get(full_remote_path,full_local_path)
		sftp.close()
		print (" --done")
		# Verify downloaded file!!
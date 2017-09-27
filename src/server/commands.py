from .file import get_folder_size
from .file import get_file_size
from .file import count_files_in_folder
from .file import get_file_hash
from src.comparators import local_and_server_files_are_equals
from src.local.file import verify_and_create_local_folder_path, local_file_exist, get_files_size_diff
from src.local.file import get_file_size as local_get_file_size
from src.server.helpers import download_server_file, upload_server_file
from src.mimes import is_jpg, is_png, is_video
from src.helpers import get_image_comp_command
import tempfile
import os

##
# Server commands
##

# Get information about the remote folder, like size and number of items
def folders_info(settings, server_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], server_rel_path)
	folder_size = get_folder_size(settings, full_path)
	num_files = count_files_in_folder(settings, full_path)
	print (" FOLDER '{}'   {} Kbytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, server_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], server_rel_path)
	file_hash = get_file_hash(settings, full_path)
	file_size = get_file_size(settings, full_path)
	print (" FILE '{}'   {} hash {} Kbytes ".format(full_path, file_hash, file_size))

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
		download_server_file(settings, full_remote_path, full_local_path)
		# sftp = settings['server_client'].client.open_sftp()
		# sftp.get(full_remote_path,full_local_path)
		# sftp.close()
		print (" --done")
		# Verify downloaded file!!

# To make it work
# sudo usermod -a -G www-data $USER
def remote_compress_images(settings, relative_path):
	full_remote_path = "{}{}".format(settings['serv-folder'],relative_path)
	if is_png(full_remote_path) or is_jpg(full_remote_path):
		print ("File {}".format(relative_path)),

		original_folder = settings["temp_folder_1"]
		comp_folder = settings["temp_folder_2"]

		temp_file = "{}/{}".format(original_folder, relative_path)
		comp_file = "{}/{}".format(comp_folder, relative_path)

		verify_and_create_local_folder_path(temp_file)
		verify_and_create_local_folder_path(comp_file)

		# Downloading file from the server
		download_server_file(settings, full_remote_path, temp_file)

		# Compressing file
		command = get_image_comp_command(temp_file, comp_file)
		if (command):
			os.system(command)
		else:
			# Redundant, we already know it is a picture
			print ("--not-image")
			return

		if (local_file_exist(comp_file)) and (int(local_get_file_size(comp_file)) > 0) :
			print ("--compressed"),
		else:
			print ("--original-file")
			os.system("cp {} {}".format(temp_file, comp_file))
			return

		# Now we show the percentage of reduction
		reduction = get_files_size_diff(temp_file, comp_file)
		print ("--reduction {}%".format(reduction)),

		if (reduction == 100):
			print ("--no-shrink")
			return

		if settings['dry-run']:
			print (" --DRY-RUN")
		else:
			# Change file permission
			settings['server_client'].execute("sudo chmod 775 '{}'".format(full_remote_path))
			# Now upload the file
			upload_server_file(settings, comp_file, full_remote_path)
			# Revert permission 
			settings['server_client'].execute("sudo chmod 755 '{}'".format(full_remote_path))
			print ("--uploaded")


from .file import get_file_size
from .file import get_folder_size
from .file import count_files_in_folder
from .file import get_file_hash

def print_path(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	print ("        '{}'   ".format(full_path))

def folders_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], local_rel_path)
	folder_size = get_folder_size(settings, full_path)
	num_files = count_files_in_folder(settings, full_path)
	print (" FOLDER '{}'   {} bytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['serv-folder'], local_rel_path)
	file_hash = get_file_hash(settings, full_path)
	file_size = get_file_size(settings, full_path)
	print (" FILE '{}'   {} hash {} bytes ".format(full_path, file_hash, file_size))

# Valid for folders and files
def get_size(settings, server_abs_path):
	command = "du --apparent-size --block-size=1 '"+server_abs_path+"' | awk '{print $1}'"
	size = settings['server_client'].execute(command)
	return size[0].rstrip()

def count_files_in_folder(settings, server_abs_path):
	command = "ls -F '{}' | grep -v / | wc -l".format(server_abs_path)
	items = settings['server_client'].execute(command)
	return items[0].rstrip()

def get_file_hash(settings, full_remote_path):
	command = "md5sum '"+full_remote_path+"' | awk '{print $1}'"
	hashForFile = settings['server_client'].execute(command)
	return hashForFile[0].rstrip()

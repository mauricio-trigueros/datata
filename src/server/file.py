def execute(settings, command):
	execution = settings['server_client'].execute(command)
	if (len(execution) > 0):
		return execution[0].rstrip()
	else :
		raise Exception("No result for command: '{}'".format(command))

def get_folder_size(settings, server_abs_path):
	command = "du -k -s '"+server_abs_path+"' | awk '{print $1}'"
	return execute(settings, command)

def get_file_size(settings, server_abs_path):
	command = "du -k '"+server_abs_path+"' | awk '{print $1}'"
	return execute(settings, command)

def count_files_in_folder(settings, server_abs_path):
	command = "ls -F '{}' | grep -v / | wc -l".format(server_abs_path)
	return execute(settings, command)

def get_file_hash(settings, full_remote_path):
	command = "md5sum '"+full_remote_path+"' | awk '{print $1}'"
	return execute(settings, command)


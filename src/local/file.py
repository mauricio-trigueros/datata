import os
import hashlib

def get_folder_size(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'], local_rel_path)
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(full_local_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size

def get_file_size(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'], local_rel_path)
	return os.path.getsize(full_local_path)

def count_files_in_folder(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'], local_rel_path)
	items = len([name for name in os.listdir(full_local_path) if os.path.isfile(os.path.join(full_local_path, name))])
	return items

def get_file_hash(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'], local_rel_path)
	return hashlib.md5(open(full_local_path,'rb').read()).hexdigest()

def local_file_exist(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'], local_rel_path)
	return os.path.isfile(full_local_path)

# If we have full file path "/var/www/project/index.html", and we want to verify that this local folder
# "/var/www/project" already exist (if LOCAL_FOLDER is /var/www/ and s3_key is project/index.html, then
# the folder "project" is not present, we need to create it)
def verify_and_create_local_folder_path(full_file_path):
	dir_name = os.path.dirname(full_file_path)
	if not os.path.isdir(dir_name):
		os.makedirs(dir_name)

def validate_local_folder_or_die(local_path):
	if not os.path.exists(local_path):
		sys.exit("path {} do not exist".format(local_path))
	else:
		return local_path
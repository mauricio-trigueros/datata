import os
import hashlib
import subprocess

def get_folder_size(abs_path):
	res =  subprocess.check_output("du -k -s '"+abs_path+"' | awk '{print $1}'", shell=True)
	return res.rstrip()

def get_file_size(abs_path):
	res =  subprocess.check_output("du -k '"+abs_path+"' | awk '{print $1}'", shell=True)
	return res.rstrip()

def count_files_in_folder(abs_path):
	items = len([name for name in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, name))])
	return items

def get_file_hash(abs_path):
	return hashlib.md5(open(abs_path,'rb').read()).hexdigest()

def local_file_exist(abs_path):
	return os.path.isfile(abs_path)

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
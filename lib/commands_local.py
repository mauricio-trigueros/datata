import os
import sys
import subprocess

def get_file_size(path):
	return os.path.getsize(path)

def validate_local_folder_or_die(local_path):
    if not os.path.exists(local_path):
        sys.exit("Local path {} do not exist".format(local_path))
    else:
        return local_path

# If we are creating file with 2019/03/moon.jpeg, folder "2019/03" should exist
def verify_and_create_folder_path(local_path):
	os.popen("mkdir -p '{}'".format(os.path.dirname(local_path)))

def is_valid_local_file(local_path):
    return os.path.isfile(local_path) and os.path.getsize(local_path) > 0

def print_size_reduction(original_path, dest_path):
    reduction = int ((float (get_file_size(dest_path)) / float (get_file_size(original_path))) * 100)
    print ("--result-size-{}%".format(reduction))

# Compress local JPG file.
def compress_local_jpg(local_path, local_dest, dry_run):
	print ("Compressing '{}' ...".format(local_path), end=' ')
	verify_and_create_folder_path(local_dest)
	command = "jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(local_path, local_dest)	
	if dry_run:
		print("--DRY-RUN")
		return	
	os.system(command)
	# Verify that file exist
	if(is_valid_local_file(local_path)):
		print("--done", end=' ')
		print_size_reduction(local_path, local_dest)
	else:
		print("--ERROR")
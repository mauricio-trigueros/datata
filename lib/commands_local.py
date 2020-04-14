import os
import sys
import tempfile
import subprocess

def get_file_size(path):
	return os.path.getsize(path)

def validate_local_folder_or_die(path):
    if not os.path.exists(path):
        sys.exit("Local path {} do not exist".format(path))
    else:
        return path

# If we are creating file with 2019/03/moon.jpeg, folder "2019/03" should exist
def verify_and_create_folder_path(path):
	os.popen("mkdir -p '{}'".format(os.path.dirname(path)))

def get_temp_file(extension=None):
    if(extension): return tempfile.NamedTemporaryFile(suffix=".{}".format(extension), delete=False)
    else: return tempfile.NamedTemporaryFile(delete=False)

def is_valid_local_file(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def print_size_reduction(origin_file_path, dest_file_path):
    reduction = int ((float (get_file_size(dest_file_path)) / float (get_file_size(origin_file_path))) * 100)
    print ("--result-size-{}%".format(reduction))

# Run a command that takes origin_file_path and produces dest_file_path (if dry_run is false)
def execute_local_command(command, origin_file_path, dest_file_path, dry_run, size_reduction=False):
	print(" Running '{}' on '{}'...".format(command.split(' ')[0], origin_file_path), end=' ')
	verify_and_create_folder_path(dest_file_path)
	if dry_run:
		print("--DRY-RUN")
		return
	os.system(command)
	# Verify that file exist
	if(is_valid_local_file(dest_file_path)):
		print("--done", end=' ')
		if size_reduction: print_size_reduction(origin_file_path, dest_file_path)
	else:
		print("--ERROR")

# Compress local JPG file.
def compress_local_jpg(origin_file_path, dest_file_path, dry_run):
	com = "jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(origin_file_path, dest_file_path)	
	execute_local_command(com, origin_file_path, dest_file_path, dry_run, size_reduction=True)

def compress_local_png(origin_file_path, dest_file_path, dry_run):
	com = "pngquant --force --quality 40-90 --speed 1 --output '{}' '{}'".format(dest_file_path, origin_file_path)
	execute_local_command(com, origin_file_path, dest_file_path, dry_run, size_reduction=True)

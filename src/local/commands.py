from .file import get_file_size
from .file import get_folder_size
from .file import count_files_in_folder
from .file import get_file_hash
from .file import get_file_size
from .file import local_file_exist
from .file import verify_and_create_local_folder_path
from src.mimes import is_jpg, is_png
import os

def print_path(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	print ("        '{}'   ".format(full_path))

def folders_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	folder_size = get_folder_size(full_path)
	num_files = count_files_in_folder(full_path)
	print (" FOLDER '{}'   {} Kbytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	file_hash = get_file_hash(full_path)
	file_size = get_file_size(full_path)
	print (" FILE '{}'   {} hash {} Kbytes ".format(full_path, file_hash, file_size))

def compress_images(settings, local_rel_path):
	local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
	print ("Compressing '{}' ".format(local_rel_path_clean)),

	original_file = "{}{}".format(settings['local'], local_rel_path_clean)
	compress_file = "{}{}".format(settings['local-dest'], local_rel_path_clean)
	
	# We need to verify that compress_file folder structure exist (may be we need to generate folders)
	verify_and_create_local_folder_path(compress_file)
	
	# First we need to delete compress_file (if already exist)
	if os.path.isfile(compress_file):
		os.remove(compress_file),
		print ("--prev-compressed-removed"),

	if is_jpg(local_rel_path):
		print ("--jpg"),
		os.system("jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(original_file, compress_file))
	elif is_png(local_rel_path):
		print ("--png"),
		os.system("pngquant --force --skip-if-larger --quality 40-100 --speed 1 --output '{}' '{}'".format(compress_file, original_file))
	else:
		print ("--not-image")
		return

	if (local_file_exist(compress_file)) and (int(get_file_size(compress_file)) > 0) :
		print ("--compressed"),
	else:
		print ("--original-file")
		os.system("cp {} {}".format(original_file, compress_file))
		return
	# Now we show the percentage of reduction
	reduction = int ((float (get_file_size(compress_file)) / float (get_file_size(original_file))) * 100)
	print ("--{}%".format(reduction))






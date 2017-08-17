import hashlib
import os
import helpers_s3
import sys

# Return the md5 of the local file passed as parameter
# We need to send a full path
def get_local_hash(full_file_path):
	return hashlib.md5(open(full_file_path,'rb').read()).hexdigest()

# If we have full file path "/var/www/project/index.html", and we want to verify that this local folder
# "/var/www/project" already exist (if LOCAL_FOLDER is /var/www/ and s3_key is project/index.html, then
# the folder "project" is not present, we need to create it)
def verify_create_local_folder_path(full_file_path):
	dir_name = os.path.dirname(full_file_path)
	if not os.path.isdir(dir_name):
		os.makedirs(dir_name)

def command_list_folder_content(settings, local_rel_path):
	print "        '{}'   ".format(local_rel_path)

# It calculates the hash of local_rel_path, and store it appends it to the hash-file
def command_calculate_hash(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'],local_rel_path)
	file_hash = get_local_hash(full_local_path)
	print "    Hash for file {} is {}".format(full_local_path, file_hash)
	f = open(settings['hash-file'], 'a')
	f.write("{} , {}\n".format(full_local_path, file_hash))
	f.close()

def command_verify_hash(settings, local_rel_path):
	full_local_path = "{}{}".format(settings['local'],local_rel_path)
	file_hash = get_local_hash(full_local_path)
	print "    Verify hash for {}".format(full_local_path),
	with open(settings['hash-file'], 'r') as f:
		for line in f:
			file_path = line.split(' , ')
			# Line found!!
			if file_path[0] == full_local_path:
				print "--hash-found",
				file_stored_hash = file_path[1][:-1] # remove last chars (new line)
				print "--same-hash" if (file_hash == file_stored_hash) else "--diff-hash"
				return
	# Line not found!
	print "--hash-not-found"

def iterator(settings, function_callback):
	print "Started iterating local folder '{}'".format(settings['local'])
	iterate_folder(settings, settings['local'],settings['prefix'],function_callback)

# Recursive function that executes function_callback with parameter file_path  against
# all the files in folder (and subfolders) set by parameter rootPath
# To execute function do_something (that takes one parameter filePath), we run it as:
# iterate_folder(settings, FOLDER, "", do_something)
# How to iterate the folders: if rootPath is /var/root/, this rootPath is always the same, we increase
# relativePath to be folderOne/, folderOne/insideOne/, ...
def iterate_folder(settings, rootPath,relativePath,functionCallback):
	# We need to concatenate the path to explore, both rootPath and relativePath ends with "/"
	folderContent = os.listdir("{}{}".format(rootPath,relativePath))
	for item in folderContent:
		# item is a folder name (without "/") or a file name
		# we calculate the absolute path of the item, and check if it is file or folder
		item_path = "{}{}{}".format(rootPath,relativePath,item)
		if os.path.isdir(item_path):
			# if item is a folder, we need to itereate again the function
			iterate_folder(
				settings,
				rootPath, # rootPath is always the same
				"{}{}/".format(relativePath,item), # relativePath is one level deeper
				functionCallback
			)
		else:
			# if item is not a folder, we assume that is a file. 
			# item_path is the full path to the file (like /home/banana/project/myfile.png)
			# but we need to send just the relative path, as we do with S3 listing, so that is project/myfile.png
			functionCallback(settings, "{}{}".format(relativePath, item))

# If local folder exist, then returns True, otherwise False
def local_path_exist(local_path):
	return os.path.exists(local_path)

def validate_local_folder_or_die(local_path):
	if not local_path_exist(local_path):
		sys.exit("path {} do not exist".format(local_path))
	else:
		return local_path

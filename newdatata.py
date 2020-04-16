import os
import sys
from lib.iterators import server_md5_files_iterator
from lib.iterators import local_md5_files_iterator
from lib.comparators import compare_file_dicts
from lib.commands_local import is_valid_local_file, compress_local_jpg, compress_local_png

from lib.actions import settings

print ("   Reading parameters from terminal....")
settings = settings()
print (settings)

# extension: file extension to filter files from settings['local-folder']
# force: if output file exist, we do nothing (unless force is true)
# command: should take as argument local_path, dest_path and dry-run
def execute_local_command(extension, force, command):
	print(" Loading {} files from {}".format(extension, settings['local-folder']))
	# First load all the files (based on the extension) where we are going to apply command.
	local_files = local_md5_files_iterator(settings['local-folder'],  extension=extension)
	if force:
		# If force, we do not care if the file exist or not, just iterate all the files and execute command
		print(" Force command")
		for re in local_files:
			local_path = local_files[re].get('full_path')
			local_dest = os.path.join(settings['local-dest'], local_files[re].get('relative_path'))
			command(local_path, local_dest, settings['dry-run'])
	else:
		# If not force, we need to get files from output folder, and check (compare_file_dicts not using MD5)
		# if the file exist or not. Then we apply command to output files that do not exist.
		print("Not forcing")
		dest_files = local_md5_files_iterator(settings['local-dest'], extension=extension)
		res = compare_file_dicts(local_files, dest_files, md5=False, verbose=False)
		for re in res:
			local_path = re.get('full_path')
			local_dest = os.path.join(settings['local-dest'], re.get('relative_path'))
			command(local_path, local_dest, settings['dry-run'])

if settings['action'] == 'download_from_server_to_local':
	print(" Downloading content from server to local...")
	remote_files = settings['server'].md5_files_iterator()
	local_files = local_md5_files_iterator(settings['local-folder'])
	res = compare_file_dicts(remote_files, local_files)
	for re in res:
		local_path = os.path.join(settings['local-folder'], re.get('relative_path'))
		settings['server'].download_file(re, local_path)
elif settings['action'] == 'upload_from_local_to_server':
	print("Uploading content from local to server ")
	remote_files = settings['server'].md5_files_iterator()
	local_files = local_md5_files_iterator(settings['local-folder'])
	res = compare_file_dicts(local_files, remote_files)
	for re in res:
		server_path = os.path.join(settings['serv-folder'], re.get('relative_path'))
		settings['server'].upload_file(re, server_path)
elif settings['action'] == 'compress_local_images':
	execute_local_command('jpg', settings['force'], compress_local_jpg)
	execute_local_command('png', settings['force'], compress_local_png)
elif settings['action'] == 's3_upload':
	print("S3 upload!!!!")
	inventory = settings['s3'].folder_iterator()
	local_files = local_md5_files_iterator(settings['local-folder'], prefix=settings['s3'].prefix)
	res = compare_file_dicts(local_files, inventory, md5=False, verbose=True)
	for re in res:
	 	print(re)
	 	settings['s3'].upload_single_file(re.get('relative_path'), re.get('full_path'), re.get('md5'))
else:
	print("No action")

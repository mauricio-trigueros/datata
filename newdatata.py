import os
import sys
from lib.iterators import server_md5_files_iterator
from lib.iterators import local_md5_files_iterator
from lib.comparators import compare_file_dicts
from lib.commands_server import download_file_from_server
from lib.commands_server import upload_file_to_server
from lib.commands_local import is_valid_local_file, compress_local_jpg

from lib.actions import settings


print ("   Reading parameters from terminal....")
settings = settings()
print (settings)

if settings['action'] == 'download_from_server_to_local':
	print(" Downloading content from server to local...")
	remote_files = server_md5_files_iterator(settings['server_client'], settings['serv-folder'])
	local_files = local_md5_files_iterator(settings['local-folder'])
	res = compare_file_dicts(remote_files, local_files)
	for re in res:
		download_file_from_server(re, settings['local-folder'], settings['server_client'], settings['dry-run'])
elif settings['action'] == 'upload_from_local_to_server':
	print("Uploading content from local to server ")
	remote_files = server_md5_files_iterator(settings['server_client'], settings['serv-folder'])
	local_files = local_md5_files_iterator(settings['local-folder'])
	res = compare_file_dicts(local_files, remote_files)
	for re in res:
		upload_file_to_server(re, settings['serv-folder'], settings['server_client'], settings['dry-run'])
elif settings['action'] == 'compress_local_images':
	# Get list of JPG files to process
	local_files = local_md5_files_iterator(settings['local-folder'], 'jpg')
	# If Force, then we need to work all the files, even if they exist
	if settings['force']:
		print(" Force compressing images")
		for re in local_files:
			local_path = local_files[re].get('full_path')
			local_dest = os.path.join(settings['local-dest'], local_files[re].get('relative_path'))
			compress_local_jpg(local_path, local_dest, settings['dry-run'])
	else:
		print(" Compressing images if do not exist")
		dest_files = local_md5_files_iterator(settings['local-dest'], 'jpg')
		res = compare_file_dicts(local_files, dest_files, False, False)
		for re in res:
			local_path = re.get('full_path')
			local_dest = os.path.join(settings['local-dest'], re.get('relative_path'))
			compress_local_jpg(local_path, local_dest, settings['dry-run'])
else:
	print("No action")

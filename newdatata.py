import os
import sys
from lib.comparators import compare_file_dicts
from lib.commands_local import LocalFile, get_temp_file
from lib.commands_server import ServerFile
from lib.actions import settings

print ("Reading parameters from terminal....")
settings = settings()

if settings['action'] == 'download_from_server_to_local':
	print(" Downloading content from server to local...")
	remote_files = settings['server'].md5_files_iterator()
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin)
	to_download = compare_file_dicts(remote_files, local_files)
	for server_file in to_download:
		downloaded_file = LocalFile(os.path.join(settings['local'].origin, server_file.relative_path))
		settings['server'].download_file(server_file, downloaded_file)

elif settings['action'] == 'upload_from_local_to_server':
	print("Uploading content from local to server ")
	remote_files = settings['server'].md5_files_iterator()
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin)
	to_upload = compare_file_dicts(local_files, remote_files)
	for local_file in to_upload:
		uploaded_file = ServerFile(settings['server'].client, os.path.join(settings['server'].folder, local_file.relative_path))
		settings['server'].upload_file(local_file, uploaded_file)

elif settings['action'] == 'compress_local_images':
	print("Compressing Local Images")
	settings['local'].compress_jpg()
elif settings['action'] == 's3_upload':
	print("S3 upload!!!!")
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin, prefix=settings['s3'].prefix)
	to_upload = compare_file_dicts(local_files, inventory, md5=False, verbose=True)
	for local_file in to_upload:
	 	settings['s3'].upload_single_file(local_file)

elif settings['action'] == 's3_download':
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin, prefix=settings['s3'].prefix) 
	to_download = compare_file_dicts(inventory, local_files, md5=False, verbose=True)
	for s3_file in to_download:
		local_file = LocalFile(os.path.join(settings['local'].origin, s3_file.relative_path))
		settings['s3'].download_single_file(s3_file, local_file)

elif settings['action'] == 'backup_database':
	db_dump = settings['mysql'].dump_database(settings['local'].origin)
	db_dump.tar(LocalFile(db_dump.path+'.tar.bz2'))
else:
	print("No action")

import os
import sys
from lib.comparators import compare_file_dicts, compare_only_missing, compare_only_different
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

elif settings['action'] == 'mirror_server_to_local':
	print("Mirror server to local file")
	remote_files = settings['server'].md5_files_iterator()
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin)
	
	to_download = compare_only_missing(remote_files, local_files, verbose=False)
	to_redownload = compare_only_different(remote_files, local_files, verbose=False)
	to_remove = compare_only_missing(local_files, remote_files, verbose=False)

	print("Downloading {} NEW server files from the server to local... ".format(len(to_download)))
	for server_file in to_download:
		local_file_path = os.path.join(settings['local'].origin, server_file.relative_path) 
		settings['server'].download_file(server_file, LocalFile(local_file_path))

	print("Removing {} local files... ".format(len(to_remove)))
	for local_file in to_remove:
		settings['local'].remove_file(local_file)

	print("Re-downloading {} DIFFERENT server files from the server to local... ".format(len(to_redownload)))
	for server_file in to_redownload:
		local_file_path = os.path.join(settings['local'].origin, server_file.relative_path)
		settings['server'].download_file(server_file, LocalFile(local_file_path))

elif settings['action'] == 'mirror_local_to_server':
	print("Mirror local to server")
	remote_files = settings['server'].md5_files_iterator()
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin)

	to_upload = compare_only_missing(local_files, remote_files, verbose=False)
	to_reupload = compare_only_different(local_files, remote_files, verbose=False)
	to_remove = compare_only_missing(remote_files, local_files, verbose=False)

	print("Uploading {} NEW files to the server...".format(len(to_upload)))
	for local_file in to_upload:
		upload_file_path = os.path.join(settings['server'].folder, local_file.relative_path)
		settings['server'].upload_file(local_file, ServerFile(settings['server'].client, upload_file_path))

	print("Removing {} server files...".format(len(to_remove)))
	for server_file in to_remove:
		settings['server'].remove_file(server_file)

	print("Re-uploading {} DIFFERENT local files... ".format(len(to_reupload)))
	for local_file in to_reupload:
		upload_file_path = os.path.join(settings['server'].folder, local_file.relative_path)
		settings['server'].upload_file(local_file, ServerFile(settings['server'].client, upload_file_path))

elif settings['action'] == 'compress_local_images':
	print("Compressing Local Images")
	settings['local'].compress_jpg()
elif settings['action'] == 's3_upload':
	print("S3 upload!!!!")
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin, prefix=settings['s3'].prefix)
	to_upload = compare_file_dicts(local_files, inventory, verbose=True)
	for local_file in to_upload:
	 	settings['s3'].upload_single_file(local_file)

elif settings['action'] == 's3_download':
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin, prefix=settings['s3'].prefix) 
	to_download = compare_file_dicts(inventory, local_files, verbose=True)
	for s3_file in to_download:
		local_file = LocalFile(os.path.join(settings['local'].origin, s3_file.relative_path))
		settings['s3'].download_single_file(s3_file, local_file)

elif settings['action'] == 'backup_database':
	db_dump = settings['mysql'].dump_database(settings['local'].origin)
	db_dump.tar(LocalFile(db_dump.path+'.tar.bz2'))
else:
	print("No action")

import os
import sys
from lib.comparators import compare_file_dicts
from lib.commands_local import LocalFile
from lib.actions import settings

print ("Reading parameters from terminal....")
settings = settings()
#print (settings)

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
	print("Compressing Local Images")
	settings['local'].compress_jpg()
elif settings['action'] == 's3_upload':
	print("S3 upload!!!!")
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = local_md5_files_iterator(settings['local-folder'], prefix=settings['s3'].prefix)
	res = compare_file_dicts(local_files, inventory, md5=False, verbose=True)
	for re in res:
	 	settings['s3'].upload_single_file(re.get('relative_path'), re.get('full_path'), re.get('md5'))
elif settings['action'] == 's3_download':
	print("S3 download!!!!")
	inventory = settings['s3'].folder_iterator(settings['s3'].prefix)
	local_files = settings['local'].local_md5_files_iterator(settings['local'].origin, prefix=settings['s3'].prefix) 
	res = compare_file_dicts(inventory, local_files, md5=False, verbose=True)
	for re in res:
	 	local_path = LocalFile(os.path.join(settings['local'].origin, re.get('relative_path')))
	 	settings['s3'].download_single_file(re, local_path)
elif settings['action'] == 'backup_database':
	db_dump = settings['mysql'].dump_database(settings['local'].origin)
	db_dump.tar(LocalFile(db_dump.path+'.tar.bz2'))
else:
	print("No action")

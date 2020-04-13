from lib.iterators import server_md5_files_iterator
from lib.iterators import local_md5_files_iterator
from lib.comparators import compare_file_dicts
from lib.commands_server import download_file_from_server
from lib.commands_server import upload_file_to_server

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
else:
	print("No action")

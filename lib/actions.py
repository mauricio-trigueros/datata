import os
import sys
from lib.comparators import compare_file_dicts, compare_only_missing, compare_only_different
from lib.commands_local import LocalClient, LocalFile, get_temp_file
from lib.commands_server import ServerClient, ServerFile
from lib.commands_s3 import S3Client
from lib.commands_mysql import MysqlClient

def compress_local_images(localClient: LocalClient):
	# First compress PNG files
	origin_files = localClient.files_iterator(localClient.origin) # Example, iterator for /home/user/a/
	dest_files = localClient.files_iterator(localClient.dest)     # Example, iterator for /home/user/b/

	target = origin_files.values() if localClient.force else compare_only_missing(origin_files, dest_files, verbose=False)

	print("Compressing {} images".format(len(target)))

	for local_file in target:
		# local_file.path can be /home/user/a/1/alfa.png and we want /home/user/b/1/alfa.png
		dest_file = LocalFile(local_file.path.replace(localClient.origin, localClient.dest))
		print("  Compressing '{}' ... ".format(local_file.path), end=' ')
		if local_file.is_image():
			print('--image ', end=' ')
			if localClient.dry_run:
				print('--DRY-RUN')
				continue
			local_file_type = local_file.get_type_by_extension()
			dest_file.verify_folder_path()
			if   local_file_type == 'gif':   local_file.compress_gif(dest_file)
			elif local_file_type == 'jpeg': local_file.compress_jpg(dest_file)
			elif local_file_type == 'png':  local_file.compress_png(dest_file)
			else: raise Exception("File {} with type {} not handled ".format(local_file.path, local_file_type))
			local_file.compare_size(dest_file)
		else:
			print('--no-image', end=' ')
		print("")

def compare_local_image_folders(localClient: LocalClient):
	origin_files = localClient.files_iterator(localClient.origin)
	dest_files = localClient.files_iterator(localClient.dest)

	for local_file in origin_files.values():
		dest_file = LocalFile(local_file.path.replace(localClient.origin, localClient.dest))
		print("Checking {} ...".format(local_file.path), end=' ')
		if local_file.is_valid():
			print('--origin-valid', end=' ')
			if local_file.is_image():
				print('--image', end=' ')
				local_file.is_valid_image_type()
		else:
			print('--ERROR-origin-not-valid', end=' ')
		if dest_file.is_valid():
			print('--destination-valid', end=' ')
			if dest_file.is_image():
				print('--image', end=' ')
				local_file.is_valid_image_type()
				local_file.compare_size(dest_file)
				local_file.compare_image_hash(dest_file)
		else:
			print('--ERROR-missing-destination!', end=' ')
		print('')

def mirror_local_folders_by_name(localClient: LocalClient):
	origin_files = localClient.files_iterator(localClient.origin)
	dest_files = localClient.files_iterator(localClient.dest)

	# We need to remove dest_files that are NOT in origin_files
	to_remove = compare_only_missing(dest_files, origin_files, verbose=False)
	print("  Found '{}' files to remove from '{}'".format(len(to_remove), localClient.dest))
	for local_file in to_remove:
		localClient.remove_file(local_file)	

def download_from_server_to_local(serverClient: ServerClient, localClient: LocalClient):
	remote_files = serverClient.md5_files_iterator()
	local_files = localClient.md5_files_iterator(localClient.origin)
	to_download = compare_file_dicts(remote_files, local_files)
	for server_file in to_download:
		downloaded_file = LocalFile(os.path.join(localClient.origin, server_file.relative_path))
		serverClient.download_file(server_file, downloaded_file)

def upload_from_local_to_server(serverClient: ServerClient, localClient: LocalClient):
	remote_files = serverClient.md5_files_iterator()
	local_files = localClient.md5_files_iterator(localClient.origin)
	to_upload = compare_file_dicts(local_files, remote_files)
	for local_file in to_upload:
		uploaded_file = ServerFile(serverClient.client, os.path.join(serverClient.folder, local_file.relative_path))
		serverClient.upload_file(local_file, uploaded_file)

def mirror_server_to_local(serverClient: ServerClient, localClient: LocalClient):
	remote_files = serverClient.md5_files_iterator()
	local_files = localClient.md5_files_iterator(localClient.origin)
	
	to_download = compare_only_missing(remote_files, local_files, verbose=False)
	to_redownload = compare_only_different(remote_files, local_files, verbose=False)
	to_remove = compare_only_missing(local_files, remote_files, verbose=False)

	print("Downloading {} NEW server files from the server to local... ".format(len(to_download)))
	for server_file in to_download:
		local_file_path = os.path.join(localClient.origin, server_file.relative_path) 
		serverClient.download_file(server_file, LocalFile(local_file_path))

	print("Removing {} local files... ".format(len(to_remove)))
	for local_file in to_remove:
		localClient.remove_file(local_file)

	print("Re-downloading {} DIFFERENT server files from the server to local... ".format(len(to_redownload)))
	for server_file in to_redownload:
		local_file_path = os.path.join(localClient.origin, server_file.relative_path)
		serverClient.download_file(server_file, LocalFile(local_file_path))

def mirror_local_to_server(serverClient: ServerClient, localClient: LocalClient):
	remote_files = serverClient.md5_files_iterator()
	local_files = localClient.md5_files_iterator(localClient.origin)

	to_upload = compare_only_missing(local_files, remote_files, verbose=False)
	to_reupload = compare_only_different(local_files, remote_files, verbose=False)
	to_remove = compare_only_missing(remote_files, local_files, verbose=False)

	print("Uploading {} NEW files to the server...".format(len(to_upload)))
	for local_file in to_upload:
		upload_file_path = os.path.join(serverClient.folder, local_file.relative_path)
		serverClient.upload_file(local_file, ServerFile(serverClient.client, upload_file_path))

	print("Removing {} server files...".format(len(to_remove)))
	for server_file in to_remove:
		serverClient.remove_file(server_file)

	print("Re-uploading {} DIFFERENT local files... ".format(len(to_reupload)))
	for local_file in to_reupload:
		upload_file_path = os.path.join(serverClient.folder, local_file.relative_path)
		serverClient.upload_file(local_file, ServerFile(serverClient.client, upload_file_path))

def s3_upload(s3client: S3Client, localClient: LocalClient):
	inventory = s3client.folder_iterator(s3client.prefix)
	local_files = localClient.md5_files_iterator(localClient.origin, prefix=s3client.prefix)
	to_upload = compare_file_dicts(local_files, inventory, verbose=True)
	for local_file in to_upload:
	 	s3client.upload_single_file(local_file)

def s3_download(s3client: S3Client, localClient: LocalClient):
	inventory = s3client.folder_iterator(s3client.prefix)
	local_files = localClient.md5_files_iterator(localClient.origin, prefix=s3client.prefix) 
	to_download = compare_file_dicts(inventory, local_files, verbose=True)
	for s3_file in to_download:
		local_file = LocalFile(os.path.join(localClient.origin, s3_file.relative_path))
		s3client.download_single_file(s3_file, local_file)

def backup_database(mysqlClient: MysqlClient, localClient: LocalClient):
	db_dump = mysqlClient.dump_database(localClient.origin)
	db_dump.tar(LocalFile(db_dump.path+'.tar.bz2'))

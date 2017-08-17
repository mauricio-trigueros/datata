import os
import paramiko
import hashlib
import sys

import helpers_local
import helpers_files

class create_ssh_client_or_die:
	client = None

	def __init__(self, server, username, password=None, key=None):
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(
			server,
			username=username,
			password=password,
			key_filename=key)
		self.client.get_transport().window_size = 3 * 1024 * 1024

	def execute(self, command):
		if(self.client):
			stdinInt, stdoutInt, stderrInt = self.client.exec_command(command)
			to_return =  stdoutInt.readlines()
			return to_return

# If item is a file, return true
# If item is a folder, return false
# If item is not a file or folder, raise an exception
def remote_item_is_file(server_client, remote_path):
	isFile =   server_client.execute("[ -f '{}' ] && echo 'true' || echo 'false'".format(remote_path))[0].rstrip()
	isFolder = server_client.execute("[ -d '{}' ] && echo 'true' || echo 'false'".format(remote_path))[0].rstrip()
	if isFile == 'true' and isFolder == 'false':
		# We are sure it is a file
		return True
	elif isFile == 'false' and isFolder == 'true':
		# We are sure it is a folder
		return False
	elif isFile == 'false' and isFolder == 'false':
		# It is not a file or a folder!
		raise "Remote file {} is not a folder or a file".format(remote_path)

def iterator(settings, function_callback):
	print "Started iterating ..."
	iterate_folder(settings, settings['serv-folder'], "", function_callback)

def iterate_folder(settings, rootPath, relativePath, functionCallback):
	remote_folder_path = "{}{}".format(rootPath,relativePath)
	folderContent = settings['server_client'].execute('ls '+remote_folder_path)
	print "Remote folder {} has items {}".format(remote_folder_path, len(folderContent))
	for index, item in enumerate(folderContent):
		item = item.rstrip() #remove last line break
		item_path = "{}{}{}".format(rootPath,relativePath,item)
		print "   Processing {}".format(item_path),
		if remote_item_is_file(settings['server_client'], item_path):
			print " --is-a-file",
			functionCallback(settings, "{}{}".format(relativePath, item))
		else:
			print " --is-a-folder"
			iterate_folder(
				settings, 
				rootPath, # rootPath is always the same
				"{}{}/".format(relativePath,item), # relativePath is one level deeper
				functionCallback
			)

def command_list_folder_content(settings, local_rel_path):
	print "        '{}'   ".format(local_rel_path)

def command_download_files(settings, relative_path):
	print " --downloading",
	full_local_path = "{}{}".format(settings['local'],relative_path)
	full_remote_path = "{}{}".format(settings['serv-folder'],relative_path)

	# Check if files are the same!!
	if helpers_files.local_and_server_files_are_equals(settings, full_local_path, full_remote_path):
		print "--untouched --DONE"
		return

	print " --downloading...",
	# If we are in dry mode, do nothing
	if settings['dry-run']:
		print " --DRY-RUN"
	else:
		helpers_local.verify_create_local_folder_path(full_local_path)
		sftp = settings['server_client'].client.open_sftp()
		sftp.get(full_remote_path,full_local_path)
		sftp.close()
		print " --done"
		# Verify downloaded file!!

def get_server_hash(server_client, full_remote_path):
	hashForFile = server_client.execute("md5sum '"+full_remote_path+"' | awk '{print $1}'")
	return hashForFile[0].rstrip()


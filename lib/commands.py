import os
import hashlib

def execute_server_command(server_client, command):
    execution = server_client.execute(command)
    if (len(execution) > 0):
        return execution[0].rstrip()
    else :
        raise Exception("No result for command: '{}'".format(command))

def get_server_file_hash(server_client, server_path):
    command = "md5sum '"+server_path+"' | awk '{print $1}'"
    return execute_server_command(server_client, command)

def download_file_from_server(file_dict, root_local, server_client, dry_run):
	local_path = os.path.join(root_local, file_dict.get('relative_path'))
	server_path = file_dict.get('full_path')
	print(" Downloading file {} -> {}...".format(server_path, local_path), end=' ')
	# If dry_run, do nothing
	if (dry_run):
		print(" --DRY-RUN")
		return
	# If we are downloading a file with path 2019/03/moon.jpeg, folder "2019/03" should exist
	os.popen("mkdir -p '{}'".format(os.path.dirname(local_path)))
	# Download the file
	print(" --downloading... ", end=' ')
	sftp = server_client.client.open_sftp()
	sftp.get(server_path, local_path)
	sftp.close()
	# Verify downloaded file hash
	downloaded_file_hash = hashlib.md5(open(local_path,'rb').read()).hexdigest()
	if downloaded_file_hash == file_dict.get('md5'):
		print(' --OK')
	else:
		print(' --ERROR')

def upload_file_to_server(file_dict, root_server, server_client, dry_run):
	local_path = file_dict.get('full_path')
	server_path = os.path.join(root_server, file_dict.get('relative_path'))
	print(" Uploading file {} -> {}...".format(local_path, server_path), end=' ')
	# If dry_run, do nothing
	if (dry_run):
		print(" --DRY-RUN")
		return
	# If we are uploading a file with path 2019/03/moon.jpeg, folder "2019/03" should exist
	server_client.execute("mkdir -p '{}'".format(os.path.dirname(server_path)))
	# Upload the file
	print(" --uploading... ", end=' ')
	sftp = server_client.client.open_sftp()
	sftp.put(local_path, server_path)
	sftp.close()
	# Verify that uploaded file hash matches local hash
	uploaded_file_hash = get_server_file_hash(server_client, server_path)
	if uploaded_file_hash == file_dict.get('md5'):
		print(' --OK')
	else:
		print(' --ERROR')

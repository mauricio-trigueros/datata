import os

def server_md5_files_iterator(server_client, remote_folder_path):
	files = {}
	# It will list all the files in current directory and subdirectories, returning file path and file MD5
	folderContent = server_client.execute("cd "+remote_folder_path+" && find -type f -exec md5sum '{}' +")
	for index, item in enumerate(folderContent):
		md5, path_temp = item.splitlines().pop().split()
		path = path_temp[2:] # path looks like "./antecesores.png", we need to remove first "./"
		parameters = {
			"md5": md5.rstrip(),
			"relative_path": path,
			"full_path": os.path.join(remote_folder_path, path)
		}
		files[path] = parameters
	return files

# If we need the iterator to run a command in local machine (like compress images), we do not need prefix.
# If we need the iterator to compare it against an S3 iterator: S3 iterator will have as relative_path 
# like "folder/in/bucket/file.extension", so we need our local iterator to have the same "relative_path",
# "folder/in/bucket/file.extension", so we need a prefix "folder/in/bucket"
def local_md5_files_iterator(local_path, prefix='.', extension='*'):
	print("Getting files iterator for path '{}' with prefix '{}' and extension '{}'".format(local_path, prefix, extension))
	files = {}
	command = "cd '"+local_path+"' && find "+prefix+" -type f -name '*."+extension+"' -exec md5 '{}' + | awk '{print $2 \" \" $4}'"
	output = os.popen(command).readlines() # Mac OS
	# Line like: MD5 (./2019/12/nasa0-320x240.jpg) = cb90cffaf3c3cb4504a381a66143d445, so with awk we select only
	# (./2019/12/nasa0-320x240.jpg) and cb90cffaf3c3cb4504a381a66143d445
	for line in output:  # or another encoding
		# First column is path (./2019/12/nasa0-320x240.jpg), and second is MD5 cb90cffaf3c3cb4504a381a66143d445
		path_temp,md5 = line.split()
		path = path_temp[1:-1] # path_temp is like (./2019/12/nasa0-320x240.jpg), remove (./)
		parameters = {
			"md5": md5.rstrip(),
			"relative_path": os.path.normpath(path),
			"full_path": os.path.normpath(os.path.join(local_path, path))
		}
		files[os.path.normpath(path)] = parameters
	return files

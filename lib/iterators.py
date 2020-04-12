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
		
def local_md5_files_iterator(local_path):
	files = {}
	output = os.popen("cd "+local_path+" && find . -type f -exec md5 '{}' +").readlines() # Mac OS
	# Line like: MD5 (./2019/12/nasa0-320x240.jpg) = cb90cffaf3c3cb4504a381a66143d445
	for line in output:  # or another encoding
		# a and b are "MD5" and "=," variables that we do not use
		a,path_temp,b,md5 = line.split()
		path = path_temp[3:-1] # path_temp is like (./2019/12/nasa0-320x240.jpg), remove (./)
		parameters = {
			"md5": md5.rstrip(),
			"relative_path": path,
			"full_path": os.path.join(local_path, path)
		}
		files[path] = parameters
	return files

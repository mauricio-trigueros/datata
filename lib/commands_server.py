import os
import hashlib
import paramiko

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

class Server:

	def __execute_command(self, command):
		execution = self.client.execute(command)
		if (len(execution) > 0):
			return execution[0].rstrip()
		else :
			raise Exception("No result for command: '{}'".format(command))

	def __init__(self, dry_run, serv_url, serv_user, serv_key, serv_folder):
		print("Creating Server...")
		self.dry_run = dry_run
		self.client = create_ssh_client_or_die(serv_url, serv_user, serv_key)
		self.folder = serv_folder

	def md5_files_iterator(self):
		files = {}
		# It will list all the files in current directory and subdirectories, returning file path and file MD5
		folderContent = self.client.execute("cd "+self.folder+" && find -type f -exec md5sum '{}' +")
		for index, item in enumerate(folderContent):
			md5, path_temp = item.splitlines().pop().split()
			path = path_temp[2:] # path looks like "./antecesores.png", we need to remove first "./"
			parameters = {
				"md5": md5.rstrip(),
				"relative_path": path,
				"full_path": os.path.join(self.folder, path)
			}
			files[path] = parameters
		return files

	def get_hash(self, server_path):
		command = "md5sum '"+server_path+"' | awk '{print $1}'"
		return self.__execute_command(command)

	def download_file(self, server_file_dict, local_path):
		print(" Downloading file {} ...".format(server_file_dict.get('relative_path')), end=' ')
		if (self.dry_run):
			print(" --DRY-RUN")
			return
		# If we are downloading a file with path 2019/03/moon.jpeg, folder "2019/03" should exist
		os.popen("mkdir -p '{}'".format(os.path.dirname(local_path)))
		# Download the file
		print(" --downloading... ", end=' ')
		sftp = self.client.client.open_sftp()
		sftp.get(server_file_dict.get('full_path'), local_path)
		sftp.close()
		# Verify downloaded file hash
		downloaded_file_hash = hashlib.md5(open(local_path,'rb').read()).hexdigest()
		if downloaded_file_hash == server_file_dict.get('md5'):
			print(' --OK')
		else:
			print(' --ERROR')

	def upload_file(self, local_file_dict, server_path):
		print(" Uploading file {} ...".format(local_file_dict.get('relative_path')), end=' ')
		if (self.dry_run):
			print(" --DRY-RUN")
			return
		# If we are uploading a file with path 2019/03/moon.jpeg, folder "2019/03" should exist
		self.client.execute("mkdir -p '{}'".format(os.path.dirname(server_path)))
		print(" --uploading... ", end=' ')
		sftp = self.client.client.open_sftp()
		sftp.put(local_file_dict.get('full_path'), server_path)
		sftp.close()
		if self.get_hash(server_path) == local_file_dict.get('md5'):
			print(' --OK')
		else:
			print(' --ERROR')

import re
import os
import hashlib
import paramiko

from lib.commands_local import LocalFile

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

class ServerFile:
	def __execute_command(self, command):
		execution = self.ssh_client.execute(command)
		if (len(execution) > 0):
			return execution[0].rstrip()
		else :
			raise Exception("No result for command: '{}'".format(command))

	def __init__(self, ssh_client, path, relative_path=None, md5=None):
		self.ssh_client = ssh_client
		self.path = path
		self.relative_path = relative_path # Subset of the path
		self.internal_md5 = md5

	def get_md5(self):
		if self.internal_md5:
			return self.internal_md5
		else:
			command = "md5sum '"+self.path+"' | awk '{print $1}'"
			return self.__execute_command(command)

class ServerClient:

	def __execute_command(self, command):
		execution = self.client.execute(command)
		if (len(execution) > 0):
			return execution[0].rstrip()
		else :
			raise Exception("No result for command: '{}'".format(command))

	def __init__(self, dry_run, serv_url, serv_user, serv_key, serv_folder):
		print("Creating Server {}@{}{}...".format(serv_user, serv_url, serv_folder))
		self.dry_run = dry_run
		self.client = create_ssh_client_or_die(serv_url, serv_user, serv_key)
		self.folder = self.check_folder_exist(serv_folder)

	def check_folder_exist(self, server_path):
		command = "test -d '"+server_path+"' ;echo $? "
		folder_is_missing = bool(int(self.__execute_command(command)))
		if folder_is_missing:
			raise Exception("Server folder '{}' is missing".format(server_path))
		return server_path

	def md5_files_iterator(self):
		files = {}
		# It will list all the files in current directory and subdirectories, returning file path and file MD5
		folderContent = self.client.execute("cd "+self.folder+" && find -type f -exec md5sum '{}' +")
		for index, item in enumerate(folderContent):
			line = item.splitlines().pop()
			# Line looks like "1704abd3d2a4d445010c678b50464345  ./2014/myfile.png"
			re_md5 = re.search('(.+?)  ', line)
			re_relpath = re.search('\.\/(.+?)$', line)
			if re_md5 and re_relpath:
				md5 = re_md5.group(1)
				relative_path = re_relpath.group(1)
				#print(" Adding server file {} with {} ".format(relative_path, md5))
				files[relative_path] = ServerFile(
					ssh_client=self.client,
					path=os.path.normpath(os.path.join(self.folder, relative_path)), # like /home/you/files/2019/12/nasa0-320x240.jpg
					relative_path=relative_path,
					md5=md5
				)
			else:
				raise Exception("Problem with line '{}' ".format(line))
		return files

	def download_file(self, server_file: ServerFile, local_file: LocalFile):
		#print(" Downloading file {} ...".format(server_file.relative_path), end=' ')
		print(" Downloading file '{}' -> '{}' ...".format(server_file.relative_path, local_file.path), end=' ')
		if (self.dry_run):
			print(" --DRY-RUN")
			return
		local_file.verify_folder_path()
		print(" --downloading... ", end=' ')
		sftp = self.client.client.open_sftp()
		sftp.get(server_file.path, local_file.path)
		sftp.close()
		if local_file.get_md5() == server_file.get_md5():
			print(' --OK')
		else:
			print(' --ERROR-WITH-MD5')

	def upload_file(self, local_file: LocalFile, server_file: ServerFile):
		print(" Uploading file {} ...".format(local_file.relative_path), end=' ')
		if (self.dry_run):
			print(" --DRY-RUN")
			return
		# If we are uploading a file with path 2019/03/moon.jpeg, folder "2019/03" should exist
		self.client.execute("mkdir -p '{}'".format(os.path.dirname(server_file.path)))
		print(" --uploading... ", end=' ')
		sftp = self.client.client.open_sftp()
		sftp.put(local_file.path, server_file.path)
		sftp.close()
		if local_file.get_md5() == server_file.get_md5():
			print(' --OK')
		else:
			print(' --ERROR-WITH-MD5')

	def remove_file(self, server_file: ServerFile):
		print(" Removing server file {} ...".format(server_file.path), end=' ')
		if self.dry_run:
			print("--DRY-RUN")
			return
		self.__execute_command("rm '{}';echo $?".format(server_file.path))
		print(' --done!')

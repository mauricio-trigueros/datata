import paramiko

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
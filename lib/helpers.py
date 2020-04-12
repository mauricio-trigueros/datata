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
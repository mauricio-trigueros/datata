import os
import sys
import tempfile
import subprocess
import hashlib

class LocalFile:
	# Path may exist (yet) or not!
	# For example, it can be the place where we will dump the database
	# (it does not exist once we create it, but it will later)
	def __init__(self, path, relative_path=None, md5=None):
		self.path = path
		self.relative_path = relative_path # Subset of the path
		self.internal_md5 = md5

	# If path is a/b/c.txt, makes sure that folders a/b exist
	def verify_folder_path(self):
		os.popen("mkdir -p '{}'".format(os.path.dirname(self.path)))

	def verify_md5(self, expected_md5):
		file_md5 = self.get_md5()
		if file_md5 != expected_md5:
			raise Exception('File {} has md5 {}, expected {}'.format(self.path, file_md5, expected_md5))

	def get_md5(self):
		if self.internal_md5:
			return self.internal_md5
		else:
			return hashlib.md5(open(self.path,'rb').read()).hexdigest()

	def get_size(self):
		return os.path.getsize(self.path)

	def is_valid(self):
		return (os.path.isfile(self.path) and os.path.getsize(self.path) > 0)

	def is_valid_or_die(self):
		if not self.is_valid():
			raise Exception("Local path {} not valid".format(self.path))

	def compare_size(self, output_file):
		reduction = int ((output_file.get_size() / self.get_size()) * 100)
		print ("--result-size-{}%".format(reduction))

	def tar(self, output_file):
		print("  Compressing '{}' ... ".format(self.path), end=' ')
		command = "tar -cpzf '{}.tar.bz2' -C / '{}' ".format(self.path, self.path)
		self.is_valid_or_die()
		os.system(command)
		self.compare_size(output_file)

class Local:
	def __init__(self, force, dry_run, local_folder, dest_folder):
		print("Creating Local for folder {}, force: {} and dry_run: {}".format(local_folder, force, dry_run))
		self.dry_run = dry_run
		self.force = force
		self.origin = self.validate_local_folder_or_die(local_folder)
		self.dest = self.validate_local_folder_or_die(dest_folder)

	def compress_jpg(self):
		print("Compressing JPGs")
		local_files = self.local_md5_files_iterator(self.origin, extension='jpg')
		for re in local_files:
			origin_file = LocalFile(local_files[re].get('full_path'))
			dest_file   = LocalFile(os.path.join(self.dest, local_files[re].get('relative_path')))
			com = "jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(origin_file.path, dest_file.path)
			self.execute_command(com, origin_file, dest_file)

	def exec(self, command, origin_file, dest_file):
		dest_file.verify_folder_path()
		os.system(command)
		dest_file.is_valid_or_die()		

	def execute_command(self, command, origin_file, dest_file):
		print(" Running '{}' on '{}'...".format(command.split(' ')[0], origin_file.path), end=' ')
		if self.dry_run:
			print("--DRY-RUN")
			return

		if not dest_file.is_valid():
			print(' --no-output-file... ', end=' ')
			self.exec(command, origin_file, dest_file)
			self.print_size_reduction(origin_file, dest_file)
			return
		
		# Dest_file exist, check we should force it or not
		if self.force:
			print(' --overwritting... ', end=' ')
			self.exec(command, origin_file, dest_file)
			self.print_size_reduction(origin_file, dest_file)
		else:
			print(' --output-file-exist-no-forcing SKIP!')

	def print_size_reduction(self, origin_file, dest_file):
		reduction = int ((dest_file.get_size() / origin_file.get_size()) * 100)
		print ("--result-size-{}%".format(reduction))

	def local_md5_files_iterator(self, local_path, prefix='.', extension='*'):
		print("Getting local files iterator for path '{}' with prefix '{}' and extension '{}'".format(local_path, prefix, extension))
		files = {}
		command = "cd '"+local_path+"' && find "+prefix+" -type f -name '*."+extension+"' -exec md5 '{}' + | awk '{print $2 \" \" $4}'"
		output = os.popen(command).readlines() # Mac OS
		# Line like: MD5 (./2019/12/nasa0-320x240.jpg) = cb90cffaf3c3cb4504a381a66143d445, so with awk we select only
		# (./2019/12/nasa0-320x240.jpg) and cb90cffaf3c3cb4504a381a66143d445
		for line in output:  # or another encoding
			# First column is path (./2019/12/nasa0-320x240.jpg), and second is MD5 cb90cffaf3c3cb4504a381a66143d445
			path_temp,md5_temp = line.split()
			relative_path = os.path.normpath(path_temp[1:-1]) # path_temp is like (./2019/12/nasa0-320x240.jpg), remove (./)
			files[relative_path] = LocalFile(
				path=os.path.normpath(os.path.join(local_path, relative_path)), # like /home/you/files/2019/12/nasa0-320x240.jpg
				relative_path=relative_path,
				md5=md5_temp.rstrip()
			)
		return files

	def validate_local_folder_or_die(self, path):
		if not os.path.exists(path):
			sys.exit("Local path {} do not exist".format(path))
		else:
			return path

def get_temp_file(extension=None) -> LocalFile:
	if(extension): 
		return LocalFile(tempfile.NamedTemporaryFile(suffix=".{}".format(extension), delete=False).name)
	else: 
		return LocalFile(tempfile.NamedTemporaryFile(delete=False).name)
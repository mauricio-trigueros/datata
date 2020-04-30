import os
import re
import sys
import tempfile
import subprocess
import hashlib
import pathlib

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

	# Return file name without extension
	def get_name(self):
		return pathlib.Path(self.path).stem

	def get_extension(self):
		return pathlib.Path(self.path).suffix

	def is_valid(self):
		return (os.path.isfile(self.path) and os.path.getsize(self.path) > 0)

	def is_valid_or_die(self):
		if not self.is_valid():
			raise Exception("Local path {} not valid".format(self.path))

	def compare_size(self, output_file):
		reduction = int ((output_file.get_size() / self.get_size()) * 100)
		print ("--result-size-{}%".format(reduction), end=' ')

	def tar(self, output_file):
		print("  Compressing '{}' ... ".format(self.path), end=' ')
		command = "tar -cpzf '{}.tar.bz2' -C / '{}' ".format(self.path, self.path)
		self.is_valid_or_die()
		os.system(command)
		self.compare_size(output_file)

	def compress_png(self, output_file):
		command = "pngquant --force --skip-if-larger --quality 40-90 --speed 1 --output '{}' '{}'".format(output_file.path, self.path)
		self.is_valid_or_die()
		os.system(command)

	def compress_jpg(self, output_file):
		command = "jpegoptim --strip-all --all-progressive --max=80 --quiet --preserve --stdout '{}' > '{}'".format(self.path, output_file.path)
		self.is_valid_or_die()
		os.system(command)

class Local:
	def __init__(self, force, dry_run, local_folder, dest_folder):
		print("  Creating Local for:\n    folder '{}'\n    force: '{}'\n    dry_run: '{}'".format(local_folder, force, dry_run))
		self.dry_run = dry_run
		self.force = force
		self.origin = self.validate_local_folder_or_die(local_folder)
		self.dest = self.validate_local_folder_or_die(dest_folder)

	def local_md5_files_iterator(self, local_path, prefix='.', extension='*'):
		print("Getting local files iterator for path '{}' with prefix '{}' and extension '{}'...".format(local_path, prefix, extension), end=' ')
		files = {}
		command = "cd '"+local_path+"' && find "+prefix+" -type f -name '*."+extension+"' -exec md5 '{}' +"
		output = os.popen(command).readlines() # Mac OS
		for line in output:  # or another encoding
			# Line like: MD5 (./2019/12/nasa0-320x240.jpg) = cb90cffaf3c3cb4504a381a66143d445
			re_md5 = re.search('\) = (.+?)$', line)
			re_relpath = re.search('\(\.\/(.+?)\) =', line)
			if re_md5 and re_relpath:
				md5 = re_md5.group(1)
				relative_path = re_relpath.group(1)
				files[relative_path] = LocalFile(
					path=os.path.normpath(os.path.join(local_path, relative_path)), # like /home/you/files/2019/12/nasa0-320x240.jpg
					relative_path=relative_path,
					md5=md5
				)
			else:
				raise Exception("Problem with line '{}' ".format(line))
		print(" returned {} items".format(len(files)))
		return files

	def validate_local_folder_or_die(self, path):
		if not os.path.exists(path):
			sys.exit("Local path {} do not exist".format(path))
		else:
			return path

	def remove_file(self, local_file: LocalFile):
		print(" Removing local file {}...".format(local_file.path), end=' ')
		if self.dry_run:
			print("--DRY-RUN")
			return
		os.remove(local_file.path)
		print(" --done!")

def get_temp_file(extension=None) -> LocalFile:
	if(extension): 
		return LocalFile(tempfile.NamedTemporaryFile(suffix=".{}".format(extension), delete=False).name)
	else: 
		return LocalFile(tempfile.NamedTemporaryFile(delete=False).name)
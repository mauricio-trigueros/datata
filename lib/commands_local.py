import os
import re
import sys
import tempfile
import subprocess
import hashlib
import pathlib
import subprocess
import imagehash
import imghdr
from PIL import Image, UnidentifiedImageError
from shutil import copyfile
from subprocess import PIPE

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

	# Return file extension, like '.gif'
	def get_extension(self):
		return pathlib.Path(self.path).suffix[1:]

	# Return type (MIME) based on extension, like 'jpeg' or 'gif'
	# Mime 'jpeg' can have different file extensions: .jpg, .jpeg, .jfif, .pjpeg, .pjp
	def get_type_by_extension(self):
		extension = self.get_extension().lower()
		if extension in ['jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp']: return 'jpeg'
		elif extension in ['png', 'gif', 'pdf', 'zip']: return extension
		else:
			return 'unknown'
			#raise Exception("Unknown type for file {}".format(self.path))

	# https://github.com/JohannesBuchner/imagehash/blob/master/imagehash.py
	def get_image_hash(self, file_path):
		return imagehash.average_hash(Image.open(file_path))

	# Return image type like: 'gif', 'jpeg', 'png' ...
	# https://docs.python.org/3.4/library/imghdr.html
	def get_image_type(self):
		return imghdr.what(self.path)

	def get_mime(self):
		image_type = self.get_image_type()
		if   image_type is 'png':    return "image/png"
		elif image_type is 'jpeg':   return "image/jpeg"
		elif image_type is 'gif':    return "image/gif"
		else: return "binary/octet-stream"

	def get_cache(self):
		file_extension = self.get_extension()
		if file_extension in ['woff']:
			return "public ,max-age= 2628000" # 1 month
		if file_extension in ['js','css']:
			return "public ,max-age= 2628000" # 1 week
		if file_extension in ['jpeg','jpg','jpe','bmp','json','svg','html', 'png']:
			return "public ,max-age= 2628000" # 1 day
		else:
			return "public"

	def is_valid_image_type(self):
		image_type = imghdr.what(self.path) # like 'gif'
		extension_type = self.get_type_by_extension() # like 'gif'
		if image_type == extension_type:
			print("--valid-image-type", end=' ')
		else:
			print("--ERROR-no-valid-type (image type: {} extension type: {})".format(image_type, extension_type), end=' ')

	# Usually we need to know if file is an image, to compress it, so we only acknowledge image types we can work with.
	def is_image(self):
		file_type = self.get_type_by_extension()
		if file_type in ['png', 'jpeg', 'gif']: return True
		else: return False

	def is_valid(self):
		try:
			valid = os.path.isfile(self.path)
			size = os.path.getsize(self.path) > 0
		except FileNotFoundError:
			return False
		return valid and size

	def is_valid_or_die(self):
		if not self.is_valid():
			raise Exception("Local path {} not valid".format(self.path))

	def compare_size(self, output_file):
		reduction = int ((output_file.get_size() / self.get_size()) * 100)
		print ("--result-size-{}%".format(reduction), end=' ')
		if reduction > 100:
			print("--ERROR-IMG-SIZE", end=' ')

	def compare_image_hash(self, output_file):
		try:
			origin_hash = self.get_image_hash(self.path)
			output_hash = self.get_image_hash(output_file.path)
			print("--img-hash-diff--{}".format((origin_hash - output_hash)), end=' ')
			if (origin_hash - output_hash) > 8:
				print("--ERROR-IMG-HASH", end=' ')
		except UnidentifiedImageError:
			print("--ERROR-IMG-HAS --format-not-valid", end=' ')

	def tar(self, output_file):
		print("  Compressing '{}' ... ".format(self.path), end=' ')
		command = "tar -cpzf '{}.tar.bz2' -C / '{}' ".format(self.path, self.path)
		self.is_valid_or_die()
		os.system(command)
		self.compare_size(output_file)

	def compress_png(self, output_file):
		command = "pngquant --force --skip-if-larger --quality 40-90 --speed 1 --output '{}' '{}' --verbose".format(output_file.path, self.path)
		self.is_valid_or_die()
		result = subprocess.run(command, stdout=PIPE, stderr=PIPE, shell=True)
		print('--compressing-png', end=' ')
		# If we can not compress the PNG (bigger size, compression out of ranges, ...)
		# then we need to copy the original image, since we always need an output file
		if 'Skipped 1 file out of a total of 1 file.' in str(result.stderr):
			print('--skipped', end=' ')
			copyfile(self.path, output_file.path)
		elif 'There were errors quantizing 1 file out of a total of 1 file' in str(result.stderr):
			print('--skipped-not-png', end=' ')
			copyfile(self.path, output_file.path)
		else:
			print('--done', end=' ')
		output_file.is_valid_or_die()

	def compress_jpg(self, output_file):
		command = "jpegoptim --strip-all --all-progressive --max=80 --verbose --preserve --stdout '{}' > '{}'".format(self.path, output_file.path)
		self.is_valid_or_die()
		result = subprocess.run(command, stdout=PIPE, stderr=PIPE, shell=True)
		print('--compressing-jpg', end=' ')
		#print(result)
		if 'skipped' in str(result.stderr):
			print('--skipped', end=' ')
			copyfile(self.path, output_file.path)
		if 'Not a JPEG file' in str(result.stderr):
			print('--skipped-not-jpg', end=' ')
			copyfile(self.path, output_file.path)
		else:
			print('--done', end=' ')
		output_file.is_valid_or_die()

	def compress_gif(self, output_file):
		command = "gifsicle -O3 --lossy=80 -o '{}' '{}'".format(output_file.path, self.path)
		self.is_valid_or_die()
		os.system(command)
		output_file.is_valid_or_die()

class LocalClient:
	def __init__(self, force, dry_run, local_folder, dest_folder):
		print("  Creating Local for:\n    folder '{}'\n    force: '{}'\n    dry_run: '{}'".format(local_folder, force, dry_run))
		self.dry_run = dry_run
		self.force = force
		self.origin = self.validate_local_folder_or_die(local_folder)
		self.dest = self.validate_local_folder_or_die(dest_folder)

	def md5_files_iterator(self, local_path, prefix='.', extension='*'):
		print("Getting MD5 iterator for path '{}' with prefix '{}' and extension '{}'...".format(local_path, prefix, extension), end=' ')
		files = {}
		command = "cd '"+local_path+"' && find "+prefix+" -type f -name '*."+extension+"' -exec md5 '{}' +"
		output = os.popen(command).readlines() # Mac OS
		for line in output:
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

	# If we need an iterator to compare with an s3 bucket, this is the scenario:
	# - File iterator for local will be: myone.png, mytwo.png, ...
	# - S3 iterator would be my/s3/folder/myfile.png, where "my/s3/folder/" is the s3prefix
	# In order to compare both dictionaries, the iterator for local will need to add the s3prefix
	def files_iterator(self, local_path, prefix='.', extension='*', s3prefix=''):
		print("Iterator for '{}' with prefix '{}' and extension '{}' and s3pref '{}'...".format(local_path, prefix, extension, s3prefix), end=' ')
		files = {}
		command = "cd '"+local_path+"' && find "+prefix+" -type f -name '*."+extension+"'"
		output = os.popen(command).readlines() # Mac OS
		for line in output:
			# Line like: ./agema-o-guardia-real-150x150.png or a/b/agema-o-guardia-real-150x150.png
			relative_path = line[2:].rstrip() if line.startswith('./') else line.rstrip()
			files[s3prefix+relative_path] = LocalFile(
				path=os.path.normpath(os.path.join(local_path, relative_path)), # like /home/you/files/2019/12/nasa0-320x240.jpg
				relative_path=relative_path
			)
		print(" returned {} items".format(len(files)))
		return files

	def validate_local_folder_or_die(self, path):
		if not os.path.exists(path):
			sys.exit("Local path {} do not exist".format(path))
		else:
			return path

	def remove_file(self, local_file: LocalFile):
		print(" Removing local file {} ...".format(local_file.path), end=' ')
		if self.dry_run: print("--DRY-RUN")
		else:
			os.remove(local_file.path)
			print(" --done!")

def get_temp_file(extension=None) -> LocalFile:
	if(extension): 
		return LocalFile(tempfile.NamedTemporaryFile(suffix=".{}".format(extension), delete=False).name)
	else: 
		return LocalFile(tempfile.NamedTemporaryFile(delete=False).name)
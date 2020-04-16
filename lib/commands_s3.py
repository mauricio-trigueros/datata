import os
import sys
import boto3
import gzip
import shutil
import botocore.exceptions

from lib.commands_local import get_temp_file, is_valid_local_file

class S3:
	# For a given key, bucket and secret, it tries to create a connection to this bucket.
	# If succed, returns a boto client object.
	# If false, returns false.
	def __create_s3_client_or_die(self, bucket, key, secret):
		client = boto3.client(
			service_name='s3',
			aws_access_key_id=key,
			aws_secret_access_key=secret,
			use_ssl=True,
		)
		try:
			client.head_bucket(Bucket=bucket)
			return client
		except botocore.exceptions.ClientError:
			sys.exit("Error with bucket, secret or key!")

	def __validate_parameter(self, name, param, options):
		if param in options: return param
		else: sys.exit("S3 parameter '{}' with value '{}' not in range {}".format(name, param, options))

	def __init__(self, dry_run, s3_bucket, s3_key, s3_secret, s3_prefix, s3_storage, s3_acl):
		self.dry_run = dry_run
		self.bucket = s3_bucket
		self.prefix = s3_prefix
		self.client = self.__create_s3_client_or_die(s3_bucket, s3_key, s3_secret)
		self.storage = self.__validate_parameter('storage', s3_storage, ['STANDARD', 'REDUCED_REDUNDANCY', 'STANDARD_IA'])
		self.acl = self.__validate_parameter('acl', s3_acl, ['private', 'public-read'])

	def folder_iterator(self, s3_folder):
		paginator = self.client.get_paginator('list_objects_v2')
		pages = paginator.paginate(Bucket=self.bucket, MaxKeys=500, StartAfter=s3_folder, Prefix=s3_folder)
		files = {}
		for page in pages:
			for obj in page['Contents']:
				# Obj like: {'Key': '..62c1.csv.gz', 'LastModified': datetime.datetime(.), 'ETag': '"04a.."', 'Size': 20, 'StorageClass': 'STANDARD'}
				parameters = {
					"md5": obj.get('ETag')[1:-1],
					"relative_path": obj.get('Key'),
					"size": obj.get('Size'),
					"modified": obj.get('LastModified'),
					"storage": obj.get('StorageClass')
				}
				files[obj.get('Key')] = parameters
		print(" found {}".format(len(files)))
		return files

	def inventory_iterator(self):
		inventory_files = self.folder_iterator(self.bucket+'/inventory/data/')		
		# Get latest inventory file
		last_inventory_file = (sorted(inventory_files.values(), key=lambda obj: obj.get('modified'), reverse=True))[0]
		print("Last inventory is {} from {}".format(last_inventory_file.get('relative_path'), last_inventory_file.get('modified')))

		# Download file to a temporal file, and extract it
		temp_gz = get_temp_file('gz')
		temp_csv = get_temp_file('csv')

		self.download_single_file(last_inventory_file, temp_gz.name)

		print("Unzipping file to {}...".format(temp_csv.name), end=' ')
		with gzip.open(temp_gz.name, 'rb') as f_in:
			with open(temp_csv.name, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
		print(" done!")

		# Read inventory file
		files = {}
		for line in open(temp_csv.name, 'r+'):
			csv_row = line.split(',') #returns a list ["1","50","60"]
			row = {}
			row['relative_path'] = csv_row[1].strip('\"')
			row['size'] = csv_row[2].strip('\"')
			row['modified'] = csv_row[3].strip('\"')
			row['md5'] = csv_row[4].strip('\"')
			row['storage'] = csv_row[5].replace('"', '').rstrip("\n\r")
			files[csv_row[1].strip('\"')] = row
		return files

	def download_single_file(self, s3_file_dict, local_path):
		print(" Downloading file {} -> {} ...".format(s3_file_dict.get('relative_path'), local_path), end=' ')
		# Check that folder path exist in local
		os.popen("mkdir -p '{}'".format(os.path.dirname(local_path)))
		# Download the file
		self.client.download_file(self.bucket, s3_file_dict.get('relative_path'), local_path)
		# Check that downloaded file is valid (check MD5!!)
		if is_valid_local_file(local_path):
			print(' done!')
		else:
			raise Exception('Error downloading file')

	def s3_upload_single_file(self, relative_path, full_path, md5):
		print (" Uploading '{}' to '{}'....".format(relative_path, self.bucket), end='')
		if self.dry_run:
			print (" --DRY-RUN")
			return
		result = self.client.put_object(
			Body = open(full_path, 'rb'),
			Bucket = self.bucket,
			Key = relative_path,
			StorageClass = self.storage,
			ACL = self.acl
			# ContentType=get_content_type_per_extension(file_extension),
			# CacheControl=get_cache_control_per_extension(file_extension)
		)
		# Compare md5 (parameter) with 'ETag', if both are the same, we are good
		if (md5 == result.get("ETag").strip('\"')):
			print(" --md5-ok")
		else:
			print(" --md5-ERROR")

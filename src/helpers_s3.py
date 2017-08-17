import boto3
import botocore.exceptions
import sys
# Import helpers
import helpers_local
import helpers_files

# Download the s3_key
def command_download_files(settings, s3_key):
	local_path = '{}{}'.format(settings['local'],s3_key)
	print " Downloading '{}' ".format(s3_key),

	# If file to download already exist and is the same, finish
	if helpers_files.local_and_s3_files_are_equals(settings, s3_key, local_path):
		print " --untouched"
		return

	print " --downloading...",
	# If we are in dry mode, do nothing
	if settings['dry-run']:
		print " --DRY-RUN"
	else:
		helpers_local.verify_create_local_folder_path(local_path)
		settings['s3_client'].download_file(settings['s3_bucket'], s3_key, local_path)
		# Now validate the downloaded file
		if helpers_files.local_and_s3_files_are_equals(settings, s3_key, local_path):
			print " --OK!"
		else:
			print " --ERROR"

# This function itereates the bucket_name passed as parameter, with the bucke_prefix.
# It needs as parameter an s3_client, that holds the credentials.
# For each s3 key, it runs function_callback, that takes 3 parameters: s3_client, bucket_name, s3_key
def iterator(settings, function_callback):
	print "Started iterating bucket {}".format(settings['s3_bucket'])
	paginator_response = settings['s3_client'].get_paginator('list_objects').paginate(Bucket=settings['s3_bucket'],MaxKeys=100,Prefix=settings['prefix'])
	for pageobject in paginator_response:
		print "----- PAGINATOR: new page ----"
		for file in pageobject["Contents"]:
			
			# Skip folders (if exist). Folders ends with "/", like "assets/"
			# files inside the folders are processed fine
			if file['Key'].endswith('/'):
				print "Skipping folder {}".format(file['Key'])
				continue

			# Now execute the callback
			function_callback(settings, file['Key'])

def command_upload_files(settings, local_rel_path):
	full_local_path = "{}{}".format(settings["local"], local_rel_path)
	file_extension = helpers_files.get_file_extension(local_rel_path)
	print " Uploading '{}' ".format(local_rel_path),
	
	# If files are the same, then they are untouched
	if helpers_files.local_and_s3_files_are_equals(settings, local_rel_path, full_local_path):
		print "--untouched --DONE"
		return
	
	# If files are differnt, we need to upload it again
	print "--uploading....",

	# If we are in dry-run, then do not run anything
	if settings['dry-run']:
		print " --DRY-RUN"
	else: 	
		result = settings['s3_client'].put_object(
			Body=open(full_local_path, 'rb'),
			Bucket=settings['s3_bucket'],
			Key=local_rel_path,
			ContentType=helpers_files.get_content_type_per_extension(file_extension),
			CacheControl=helpers_files.get_cache_control_per_extension(file_extension)
		)
		
		# Now we need to validate the upload
		if (helpers_local.get_local_hash(full_local_path) == result['ETag'][1:-1]):
			print "--verified --DONE"
			return
		else:
			print "--ERROR --DONE"
			raise "File {} uploaded with errors!!".format(full_local_path)

def command_list_bucket_content(settings, s3_key):
	print "        '{}'   ".format(s3_key)

# Takes as parameter an S3 key (like "assets/images/size/pique/papa/moon.png") and adds a cache to this file
# It always adds a cache-control, based on file_extension
# If not file_extension is found, it adds the default cache-control
def command_set_cache_control(settings, s3_key):
	file_extension = helpers_files.get_file_extension(s3_key)
	cache_control  = helpers_files.get_cache_control_per_extension(file_extension)
	# If the file extension is not recognized, then cache_control is false, we can not add cache to a file type that 
	# we do not know (it does not match any file known file extension)
	print "        '{}'   ".format(s3_key, file_extension),
	
	# If Cache control is the same, then do not touch anything
	s3_object = settings['s3_client'].get_object(Bucket=settings["s3_bucket"], Key=s3_key)
	if ('CacheControl' in s3_object) and (s3_object['CacheControl'] == cache_control):
		print " --same-cache-control"
		return

	print " --adding-cache-control...",

	# If we are in dry-run, then do not run anything
	if settings['dry-run']:
		print " --DRY-RUN"
	else: 	
		# If CacheControl is different, and we are not in dry-run mode
		result = settings['s3_client'].copy_object(
			Bucket = settings["s3_bucket"],
			Key = s3_key,
			ContentType=s3_object['ContentType'], # keep content type!
			CacheControl=cache_control,
			CopySource = settings["s3_bucket"]+"/"+s3_key,
			Metadata = s3_object['Metadata'],
			MetadataDirective='REPLACE'
		)
		print " --http-status={}".format(result['ResponseMetadata']['HTTPStatusCode'])


# Sets the mime type of the S3 key passed as parameter (like "assets/images/size/pique/papa/moon.png")
# Usually the mime type is set when we upload the file, based on extension, but this is not alwasy the case.
# If we want to add the mimetype "image/png" to file extension "xx": then add it to get_content_type_per_extension
def command_set_file_mime_type(settings, s3_key):
	# First get the file details from S3
	s3_object = settings['s3_client'].get_object(Bucket=settings['s3_bucket'], Key=s3_key)
	file_extension = helpers_files.get_file_extension(s3_key)
	mime_guessed   = helpers_files.get_content_type_per_extension(file_extension)

	print " Adding mime to '{}' ".format(s3_key),

	# If we do not recognize the extension (can be missing, wrong, or not set in this app), we can not set the mime_type
	if mime_guessed == "binary/octet-stream":
		print "--unknown-mime"
		return

	# If the mime we guess (mime_guessed) is the same than the one in the s3_object, then we do not touch it
	if mime_guessed == s3_object['ContentType']:
		print "--unchanged-mime"
		return

	# If remote file has a mime type different than default one ('binary/octet-stream'), do not touch it, probably is valid
	if s3_object['ContentType'] != 'binary/octet-stream':
		print "--valid-remote-mime",

	print "--setting-mime...",

	# If we are in dry mode, do nothing
	if settings['dry-run']:
		print " --DRY-RUN"
	else:
		result = settings['s3_client'].copy_object(
			Bucket = settings["s3_bucket"],
			Key = s3_key,
			ContentType=mime_guessed,
			CopySource = settings["s3_bucket"]+"/"+s3_key,
			Metadata = s3_object['Metadata'],
			MetadataDirective='REPLACE'
		)
		print " --http-status={}".format(result['ResponseMetadata']['HTTPStatusCode'])

# For a given key, bucket and secret, it tries to create a connection to this bucket.
# If succed, returns a boto client object.
# If false, returns false.
def create_s3_client_or_die(key, bucket, secret):
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



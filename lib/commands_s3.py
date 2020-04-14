import sys
import boto3
import gzip
import shutil
import botocore.exceptions

from lib.commands_local import get_temp_file, is_valid_local_file

# For a given key, bucket and secret, it tries to create a connection to this bucket.
# If succed, returns a boto client object.
# If false, returns false.
def create_s3_client_or_die(bucket, key, secret):
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

# Return iterator, the list of files, given the s3_folder
def s3_folder_iterator(s3_client, bucket, s3_folder):
	print(" Getting file list for bucket '{}' and folder '{}'...".format(bucket, s3_folder), end=' ')
	paginator = s3_client.get_paginator('list_objects_v2')
	pages = paginator.paginate(Bucket=bucket, MaxKeys=500, StartAfter=s3_folder, Prefix=s3_folder)
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

# Returns a list with all the bucket stuff
def s3_inventory_iterator(bucket, s3_client, prefix):
	inventory_folder = "{}/inventory/data/".format(bucket)
	inventory_files = s3_folder_iterator(s3_client, bucket, inventory_folder)

	# Get latest inventory file
	last_inventory_file = (sorted(inventory_files.values(), key=lambda obj: obj.get('modified'), reverse=True))[0]
	print("Last inventory is {} from {}".format(last_inventory_file.get('relative_path'), last_inventory_file.get('modified')))

	# Download file to a temporal file, and extract it
	temp_gz = get_temp_file('gz')
	temp_csv = get_temp_file('csv')
	print("Downloading inventory to '{}'...".format(temp_gz.name), end=' ')
	s3_client.download_file(bucket, last_inventory_file.get('relative_path'), temp_gz.name)
	if is_valid_local_file(temp_gz.name):
		print(' done!')
	else:
		print(' error!')
		return
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

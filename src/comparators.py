from src.local.file import get_file_hash
from src.local.file import local_file_exist
from botocore.exceptions import ClientError

# Compares if two files, one in S3 bucket, and one in local, are the same
# relative_path is the S3 key
def local_and_s3_files_are_equals(settings, relative_path):
	# If local file do not exist, then files are not equals!!
	if not local_file_exist(settings, relative_path):
		print ("--local-missing"),
		return False
	# Try to get remote file
	try:
		remote_object = settings['s3_client'].head_object(Bucket=settings['s3_bucket'],Key=relative_path)
	except ClientError as e:
		if e.response['Error']['Code'] == "404":
			print ("--s3-missing"),
			return False
		else:
			print ("we have an error!")
			print (e)
			raise 'error'

	# Local file and S3 file exist, compare etags
	if (get_file_hash(settings, relative_path) == remote_object['ETag'][1:-1]):
		print ("--same-hash"),
		return True
	else:
		print ("--different-hash"),
		return False

def local_and_server_files_are_equals(settings, full_local_path, full_remote_path):
	# If local file do not exist, then files are not equals!!
	if not os.path.isfile(full_local_path):
		print ("--local-missing"),
		return False

	if (helpers_local.get_local_hash(full_local_path) == server_file.get_file_hash(settings, full_remote_path)):
		print ("--same-hash"),
		return True
	else:
		print ("--different-hash"),
		return False
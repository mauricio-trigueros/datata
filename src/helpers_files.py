import os.path
from botocore.exceptions import ClientError
# Import helpers
import helpers_local
import helpers_s3
import helpers_server

# Compares hashes of s3_key and local_path
# If files are the same (same hash) then return True
# If files are different (or one do not exist), then return false
def local_and_s3_files_are_equals(settings, s3_key, local_path):
	# If local file do not exist, then files are not equals!!
	if not os.path.isfile(local_path):
		print "--local-missing",
		return False
	# Try to get remote file
	try:
		remote_object = settings['s3_client'].head_object(Bucket=settings['s3_bucket'],Key=s3_key)
	except ClientError as e:
		if e.response['Error']['Code'] == "404":
			print "--s3-missing",
			return False
		else:
			print "we have an error!"
			print e
			raise 'error'

	# Local file and S3 file exist, compare etags	
	if (helpers_local.get_local_hash(local_path) == remote_object['ETag'][1:-1]):
		print "--same-hash",
		return True
	else:
		print "--different-hash",
		return False

def local_and_server_files_are_equals(settings, full_local_path, full_remote_path):
	# If local file do not exist, then files are not equals!!
	if not os.path.isfile(full_local_path):
		print "--local-missing",
		return False

	if (helpers_local.get_local_hash(full_local_path) == helpers_server.get_server_hash(settings['server_client'], full_remote_path)):
		print "--same-hash",
		return True
	else:
		print "--different-hash",
		return False

# Takes as parameter a file extension in downcase (mp3, jpg, ....)
# and return the Cache control associated to this file extension.
# It ALWAYS need to return a valid Cache Control value
def get_cache_control_per_extension(file_extension):
	if file_extension in ['woff']:
		return "public ,max-age= 2628000" # 1 month
	if file_extension in ['js','css']:
		return "public ,max-age= 604800" # 1 week
	if file_extension in ['jpeg','jpg','jpe','bmp','json','svg','html', 'png']:
		return "public ,max-age= 604800" # 1 day
	else:
		return "public"

def get_file_extension(file_path):
	return os.path.splitext(file_path)[1][1:].lower()

# Based on list: http://svn.apache.org/viewvc/httpd/httpd/trunk/docs/conf/mime.types?view=markup
# It ALWAYS need to return a valid mime type
def get_content_type_per_extension(file_extension):
	if   file_extension in ['png']:                   return "image/png"
	elif file_extension in ['jpeg','jpg','jpe']:      return "image/jpeg"
	elif file_extension in ['bmp']:                   return "image/bmp"
	elif file_extension in ['css']:                   return "text/css"
	elif file_extension in ['csv']:                   return "text/csv"
	elif file_extension in ['html','htm']:            return "text/html"
	elif file_extension in ['json']:                  return "application/json"
	elif file_extension in ['js']:                    return "application/javascript"
	elif file_extension in ['svg']:                   return "image/svg+xml"
	else: return "binary/octet-stream"
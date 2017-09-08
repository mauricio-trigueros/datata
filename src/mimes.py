import os

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

def is_png(file_path):
	extension = get_file_extension(file_path).lower()
	if extension in ['png']:  return True
	else: return False

def is_jpg(file_path):
	extension = get_file_extension(file_path).lower()
	if extension in ['jpeg','jpg','jpe']:  return True
	else: return False
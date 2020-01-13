import os

# Takes as parameter a file extension in downcase (mp3, jpg, ....)
# and return the Cache control associated to this file extension.
# It ALWAYS need to return a valid Cache Control value
def get_cache_control_per_extension(file_extension):
    if file_extension in ['woff']:
        return "public ,max-age= 2628000" # 1 month
    if file_extension in ['js','css']:
        return "public ,max-age= 2628000" # 1 week
    if file_extension in ['jpeg','jpg','jpe','bmp','json','svg','html', 'png']:
        return "public ,max-age= 2628000" # 1 day
    else:
        return "public"

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1][1:].lower()

# Check if the file is suitable to be uploaded.
# For example, ".DS_Store" files are forbidden to upload
def forbidden_to_upload(file_path):
    # Reject ".DS_Store", "lala/.DS_Store" and similiar
    if(file_path.endswith('.DS_Store')):
        return True
    else:
        return False

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

# Particular file type checkers
def is_png(file_path):
    extension = get_file_extension(file_path).lower()
    if extension in ['png']:  return True
    else: return False

def is_jpg(file_path):
    extension = get_file_extension(file_path).lower()
    if extension in ['jpeg','jpg','jpe']:  return True
    else: return False

# General file type checkers
def is_image(file_path):
    if is_png(file_path) or is_jpg(file_path):
        return True
    else: return False

def is_video(file_path):
    extension = get_file_extension(file_path).lower()
    if extension in ['mp4', 'avi', 'mov', 'divx', 'flv']:  return True
    else: return False

def is_zip(file_path):
    extension = get_file_extension(file_path)
    if extension in ['gz']:  return True
    else: return False

def is_pdf(file_path):
    extension = get_file_extension(file_path)
    if extension in ['pdf']: return True
    else: return False

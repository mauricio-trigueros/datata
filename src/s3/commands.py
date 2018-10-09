import tempfile
from src.comparators import local_and_s3_equals
from src.local.file import verify_and_create_local_folder_path
from src.local.file import get_file_hash
from src.local.file import get_temp_file
from src.local.file import unzip_file_to_temp
from src.mimes import get_file_extension
from src.mimes import get_content_type_per_extension
from src.mimes import get_file_extension
from src.mimes import get_cache_control_per_extension
from src.mimes import forbidden_to_upload
from src.mimes import is_zip

def print_path(settings, s3_key):
    print ("        '{}'   ".format(s3_key))

def download_files(settings, s3_key):
    print (" Downloading '{}' ".format(s3_key), end='')
    full_local_path = "{}{}".format(settings['local'], s3_key)

    # If file to download already exist and is the same, finish
    if local_and_s3_equals(settings, full_local_path, s3_key):
        print (" --untouched")
        return

    print (" --downloading...", end='')
    # If we are in dry mode, do nothing
    if settings['dry-run']:
        print (" --DRY-RUN")
    else:
        # local_path is where we will downlad the file in local
        verify_and_create_local_folder_path(full_local_path)
        settings['s3_client'].download_file(settings['s3_bucket'], s3_key, full_local_path)
        # Now validate the downloaded file
        if local_and_s3_equals(settings, full_local_path, s3_key):
            print (" --OK!")
        else:
            print (" --ERROR")

def upload_files(settings, local_rel_path):
    full_local_path = "{}{}".format(settings["local"], local_rel_path)
    s3_path = "{}{}".format(settings['s3-prefix'], local_rel_path)
    file_extension = get_file_extension(local_rel_path)
    print (" Uploading '{}' -> {} ".format(local_rel_path, s3_path), end='')

    if forbidden_to_upload(full_local_path):
        print ("--forbidden-to-upload")
        return
    
    # If files are the same, then they are untouched
    if local_and_s3_equals(settings, full_local_path, s3_path):
        print ("--untouched --DONE")
        return
    
    # If files are differnt, we need to upload it again
    print ("--uploading....", end='')

    # If we are in dry-run, then do not run anything
    if settings['dry-run']:
        print (" --DRY-RUN")
    else:   
        result = settings['s3_client'].put_object(
            Body=open(full_local_path, 'rb'),
            Bucket=settings['s3_bucket'],
            Key=s3_path,
            StorageClass="STANDARD_IA",
            ContentType=get_content_type_per_extension(file_extension),
            CacheControl=get_cache_control_per_extension(file_extension)
        )
        
        # Now we need to validate the upload
        if (get_file_hash(full_local_path) == result['ETag'][1:-1]):
            print ("--verified --DONE")
            return
        else:
            print ("--ERROR --DONE")
            raise "File {} uploaded with errors!!".format(full_local_path)

# Takes as parameter an S3 key (like "assets/images/size/pique/papa/moon.png") and adds a cache to this file
# It always adds a cache-control, based on file_extension
# If not file_extension is found, it adds the default cache-control
def set_cache_control(settings, s3_key):
    file_extension = get_file_extension(s3_key)
    cache_control  = get_cache_control_per_extension(file_extension)
    # If the file extension is not recognized, then cache_control is false, we can not add cache to a file type that 
    # we do not know (it does not match any file known file extension)
    print ("        '{}'   ".format(s3_key, file_extension), end='')
    
    # If Cache control is the same, then do not touch anything
    s3_object = settings['s3_client'].get_object(Bucket=settings["s3_bucket"], Key=s3_key)
    if ('CacheControl' in s3_object) and (s3_object['CacheControl'] == cache_control):
        print (" --same-cache-control")
        return

    print (" --adding-cache-control...", end='')

    # If we are in dry-run, then do not run anything
    if settings['dry-run']:
        print (" --DRY-RUN")
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
        print (" --http-status={}".format(result['ResponseMetadata']['HTTPStatusCode']))

# Sets the mime type of the S3 key passed as parameter (like "assets/images/size/pique/papa/moon.png")
# Usually the mime type is set when we upload the file, based on extension, but this is not alwasy the case.
# If we want to add the mimetype "image/png" to file extension "xx": then add it to get_content_type_per_extension
def set_mime_type(settings, s3_key):
    # First get the file details from S3
    s3_object = settings['s3_client'].get_object(Bucket=settings['s3_bucket'], Key=s3_key)
    file_extension = get_file_extension(s3_key)
    mime_guessed   = get_content_type_per_extension(file_extension)

    print (" Adding mime to '{}' ".format(s3_key), end='')

    # If we do not recognize the extension (can be missing, wrong, or not set in this app), we can not set the mime_type
    if mime_guessed == "binary/octet-stream":
        print ("--unknown-mime")
        return

    # If the mime we guess (mime_guessed) is the same than the one in the s3_object, then we do not touch it
    if mime_guessed == s3_object['ContentType']:
        print ("--unchanged-mime")
        return

    # If remote file has a mime type different than default one ('binary/octet-stream'), do not touch it, probably is valid
    if s3_object['ContentType'] != 'binary/octet-stream':
        print ("--valid-remote-mime", end='')

    print ("--setting-mime...", end='')

    # If we are in dry mode, do nothing
    if settings['dry-run']:
        print (" --DRY-RUN")
    else:
        result = settings['s3_client'].copy_object(
            Bucket = settings["s3_bucket"],
            Key = s3_key,
            ContentType=mime_guessed,
            CopySource = settings["s3_bucket"]+"/"+s3_key,
            Metadata = s3_object['Metadata'],
            MetadataDirective='REPLACE'
        )
        print (" --http-status={}".format(result['ResponseMetadata']['HTTPStatusCode']))

# For example, we wanth the last objects for folder:
# mybucketname/myfolder/myfolder.csv/data/inventory_papapapa.csv.gz
# Then folder is "mybucketname/myfolder/myfolder.csv/data/" and prefix is "inventory_"
def get_s3_latest_object(settings, folder, prefix):
    # print("PRINT")
    # print("{}/inventory_".format(folder))
    # print("mydemotestbucket2/mytestinventory.csv/data/inventory_")
    resp = settings['s3_client'].list_objects_v2(
        Bucket=settings['s3_bucket'],
        MaxKeys=100,
        StartAfter="{}/{}".format(settings['s3_bucket'],folder),
        Prefix="{}/{}".format(folder, prefix),
    )
    print(resp)
    last = (sorted(resp['Contents'], key=lambda obj: obj['LastModified'], reverse=True))[0]
    return last

# Returns a zip
def get_unzipped_s3_file(settings, key):
    print("Downloading file {} ".format(key))
    extension = get_file_extension(key)
    temp_download = get_temp_file(extension)
    print(extension)
    print(temp_download)
    # Download file
    settings['s3_client'].download_file(settings['s3_bucket'], key, temp_download.name)
    # Check if is zip file
    if(is_zip(temp_download.name)):
        print("File is zip!")
        unzip = unzip_file_to_temp(temp_download.name)
        print("Unzipped to {}".format(unzip.name))
        return unzip
    return None

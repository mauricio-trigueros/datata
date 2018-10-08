from src.local.file import get_file_hash as get_local_file_hash
from src.server.file import get_file_hash as get_server_file_hash
from src.local.file import local_file_exist
from botocore.exceptions import ClientError

def local_and_s3_equals(settings, full_local_path, full_s3_path):
    if not local_file_exist(full_local_path):
        print ("--local-missing", end='')
        return False
    # Try to get remote file
    try:
        remote_object = settings['s3_client'].head_object(Bucket=settings['s3_bucket'],Key=full_s3_path)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print ("--s3-missing", end='')
            return False
        else:
            print ("we have an error!")
            raise Exception(e.message)

    # Local file and S3 file exist, compare etags
    if (get_local_file_hash(full_local_path) == remote_object['ETag'][1:-1]):
        print ("--same-hash", end=' ')
        return True
    else:
        print ("--different-hash", end=' ')
        return False

def local_and_server_files_are_equals(settings, full_local_path, full_remote_path):
    # If local file do not exist, then files are not equals!!
    if not local_file_exist(full_local_path):
        print ("--local-missing", end=' ')
        return False

    if (get_local_file_hash(full_local_path) == get_server_file_hash(settings, full_remote_path)):
        print ("--same-hash", end=' ')
        return True
    else:
        print ("--different-hash", end=' ')
        return False
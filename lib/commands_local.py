import os
import sys

def validate_local_folder_or_die(local_path):
    if not os.path.exists(local_path):
        sys.exit("Local path {} do not exist".format(local_path))
    else:
        return local_path
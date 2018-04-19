from .file import get_file_size
from .file import get_folder_size
from .file import count_files_in_folder
from .file import get_file_hash
from .file import get_file_size
from .file import local_file_exist
from .file import verify_and_create_local_folder_path
from .file import get_files_size_diff
from src.mimes import is_jpg, is_png, is_video, get_file_extension
from src.helpers import get_image_comp_command
import os
import sys
import tempfile
from .helpers import execute_command_according_strategy

def print_path(settings, local_rel_path):
    full_path = "{}{}".format(settings['local'], local_rel_path)
    print ("        '{}'   ".format(full_path))

def folders_info(settings, local_rel_path):
    full_path = "{}{}".format(settings['local'], local_rel_path)
    folder_size = get_folder_size(full_path)
    num_files = count_files_in_folder(full_path)
    print (" FOLDER '{}'   {} Kbytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, local_rel_path):
    full_path = "{}{}".format(settings['local'], local_rel_path)
    file_hash = get_file_hash(full_path)
    file_size = get_file_size(full_path)
    print (" FILE '{}'   {} hash {} Kbytes ".format(full_path, file_hash, file_size))

# To use this command we need to use "images" iterator, we we are sure that local_rel_path is a picture.
def compress_images(settings, local_rel_path):
    local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
    print ("Compressing '{}' ".format(local_rel_path_clean)),

    original_file = "{}{}".format(settings['local'], local_rel_path_clean)
    compress_file = "{}{}".format(settings['local-dest'], local_rel_path_clean)
    
    # We need to verify that compress_file folder structure exist (may be we need to generate folders)
    verify_and_create_local_folder_path(compress_file)

    # Get the command to execute, if JPG or PNG, or return if no picture
    command = get_image_comp_command(original_file, compress_file)
    execute_command_according_strategy(command, settings, compress_file, original_file)

def tar_files(settings, local_rel_path):
    local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
    extension = get_file_extension(local_rel_path_clean)
    print ("Compressing '{}' with extension '{}' ".format(local_rel_path_clean, extension)),
    # If file is already compressed (or has no extension) skip it
    if extension in ['bz2', 'zip', '']:
        print ('--file-already-compressed --DONE')
        return

    original_file = "{}{}".format(settings['local'], local_rel_path_clean)
    compress_file = "{}{}".format(settings['local-dest'], "{}.tar.bz2".format(local_rel_path_clean))

    command = "tar -cpzf '{}' -C / '{}' ".format(compress_file, original_file[1:])
    execute_command_according_strategy(command, settings, compress_file, original_file)

def verify_videos(settings, local_rel_path):
    local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
    full_path = "{}{}".format(settings['local'], local_rel_path_clean)

    if is_video(local_rel_path):
        print ("Verifying video '{}' ".format(full_path)),
        # Create temporal file to keep the check result (we will remove it later)
        temp_file, temp_file_path = tempfile.mkstemp()
        command = "ffmpeg -v error -i '{}' -f null - 2>'{}'".format(full_path, temp_file_path)
        # Execute command
        result = os.system(command)
        # Check file size
        if (int(get_file_size(temp_file_path)) > 0):
            print ("--video-PROBLEM")
        else:
            print ("--video-OK")
        os.close(temp_file)






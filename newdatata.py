from lib.settings import settings
from lib.actions import *

print ("\n### Reading parameters from terminal....")
settings = settings()

print("\n### Executing action: '{}'".format(settings['action']))
print(settings['description'])

if   settings['action'] == 'download_from_server_to_local': download_from_server_to_local(settings['server'], settings['local'])
elif settings['action'] == 'upload_from_local_to_server':   upload_from_local_to_server(settings['server'], settings['local'])
elif settings['action'] == 'mirror_server_to_local':        mirror_server_to_local(settings['server'], settings['local'])
elif settings['action'] == 'mirror_local_to_server':        mirror_local_to_server(settings['server'], settings['local'])
elif settings['action'] == 'mirror_local_folders_by_name':  mirror_local_folders_by_name(settings['local'])
elif settings['action'] == 'mirror_local_to_s3':            mirror_local_to_s3(settings['s3'], settings['local'])
elif settings['action'] == 'compress_local_images':         compress_local_images(settings['local'])
elif settings['action'] == 'compare_local_image_folders':   compare_local_image_folders(settings['local'])
elif settings['action'] == 's3_upload':                     s3_upload(settings['s3'], settings['local'])
elif settings['action'] == 's3_download':                   s3_download(settings['s3'], settings['local'])
elif settings['action'] == 'backup_database':               backup_database(settings['mysql'], settings['local'])
else: print("No action")

print("\n### Done!!")

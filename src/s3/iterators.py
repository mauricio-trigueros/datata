from .helpers import get_bucket_inventory

# This function itereates the bucket_name passed as parameter, with the bucke_prefix.
# It needs as parameter an s3_client, that holds the credentials.
# For each s3 key, it runs function_callback, that takes 3 parameters: s3_client, bucket_name, s3_key
def iterator(settings, function_callback):
    print ("Started iterating bucket {}".format(settings['s3_bucket']))
    paginator_response = settings['s3_client'].get_paginator('list_objects').paginate(Bucket=settings['s3_bucket'],MaxKeys=100,Prefix=settings['prefix'])
    for pageobject in paginator_response:
        print ("----- PAGINATOR: new page ----")
        for file in pageobject["Contents"]:
            
            # Skip folders (if exist). Folders ends with "/", like "assets/"
            # files inside the folders are processed fine
            if file['Key'].endswith('/'):
                print ("Skipping folder {}".format(file['Key']))
                continue

            # Now execute the callback
            function_callback(settings, file['Key'])

def iterator_inventory(settings, function_callback):
    print ("Iterating with inventory")
    inventory = get_bucket_inventory(settings)
    print ("Got inventory, starting loop")
    for item in inventory:
        print ("{} | {} bytes | {} | {} ".format(item['file'], item['size'], item['md5'], item['storage']))
    return


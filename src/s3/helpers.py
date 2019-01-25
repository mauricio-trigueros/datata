import boto3
import botocore.exceptions
import sys
from .commands import get_s3_latest_object, get_unzipped_s3_file

# For a given key, bucket and secret, it tries to create a connection to this bucket.
# If succed, returns a boto client object.
# If false, returns false.
def create_s3_client_or_die(key, bucket, secret):
    client = boto3.client(
        service_name='s3',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        use_ssl=True,
    )
    try:
        client.head_bucket(Bucket=bucket)
        return client
    except botocore.exceptions.ClientError:
        sys.exit("Error with bucket, secret or key!")

# Returns a list with all the bucket stuff
def get_bucket_inventory(settings):
    inventory_folder = "{}/inventory/data".format(settings['s3_bucket'])
    # First get last inventory s3-object
    inventory_s3_object = get_s3_latest_object(settings, inventory_folder, '')
    print("Last inventory is {} from {}".format(inventory_s3_object['Key'], inventory_s3_object['LastModified']))
    # Download it and unzip it if need it
    file = get_unzipped_s3_file(settings, inventory_s3_object['Key'])
    # Now we have the unzipped file!
    inventory = []
    for line in open(file.name, 'r+'):
        csv_row = line.split(',') #returns a list ["1","50","60"]
        row = {}
        row['file'] = csv_row[1].strip('\"')
        row['size'] = csv_row[2].strip('\"')
        row['md5'] = csv_row[4].strip('\"')
        row['storage'] = csv_row[5].replace('"', '').rstrip("\n\r")
        inventory.append(row)
    return inventory

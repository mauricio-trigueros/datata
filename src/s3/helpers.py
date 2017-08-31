import boto3
import botocore.exceptions
import sys

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



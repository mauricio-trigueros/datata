# Datata

Datata is a tool to work with data. The main goal is to pull/push data from/to servers, S3 buckets, databases.... and also to process these data (for example compressing pictures).

It is written in Python, and tested in Mac OS Sierra.

It is designed to execute commands in one single line. For example, to list the current directory, the command look like:
```
python datata.py --command="list_local_folder" --local="."
```

## Installing Datata

1. You need *virtualenv* installed in your computer. 
```
pip install virtualenv
```

2. Then create a Python virtual enviroment.
```
virtualenv venv
```

3. Load the virtualenvironment that you just created.
```
source venv/bin/activate
```

4. And populate it with the requirements file.
```
pip install -r requirements.txt
```

5. And now you are able to run the commands, for example lets list the content of our current directory:
```
python datata.py --command="list_local_folder" --local="."
```

Now you are able to run any other command.

### Dependencies

For certain commands, you need to install some files / programs.
For example:

- To use the command **mysql_full_backup**, you need to install *mysqldump* in your computer.
- To use the command **compress_images**, you need to install *pngquant* and *jpegoptim*.

## List of commands to execute:
To see all commands that you can execute, with an example and a small description, just run:
```
python datata.py --command="list_commands"
```

The result will be something like:
```
  Command: set_s3_cache_control
    Set the Cache-Control header, for "bucket" (with "prefix"). Cache-Control is set in "helpers_files.py", method "get_cache_control_per_extension". If "dry-run" is True, files will not be affected, just listed.
    Mandatory values: ['secret', 'key', 'bucket', 'dry-run']
    Example: python datata.py --command="set_s3_cache_control" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"

  Command: calculate_hash
    Calculate hash for local files "local", and leave the result in "hash-file". This "hash-file" needs to exist, and hashes will be appended to the end of file.
    Mandatory values: ['local', 'hash-file']
    Example: python datata.py --command="calculate_hash" --local="/Users/me/folder" --hash-file="/Users/me/Downloads/hash.txt"

  Command: mysql_full_backup
    Perform a full MySQL database dump to folder "local", with SQL file name "mysql_full_backup_DATE.sql".
    Mandatory values: ['local', 'mysql-host', 'mysql-port', 'mysql-user', 'mysql-pass', 'mysql-db']
    Example: python datata.py --command="mysql_full_backup" --local="/Users/me/folder" --mysql-host="192.168.100.72" --mysql-port="3306" --mysql-user="dev-user" --mysql-pass="dev-pass" --mysql-db="mydb"

  Command: verify_hash
    Validate if hash calculated with command "calculate_hash" matches the files.
    Mandatory values: ['local', 'hash-file']
    Example: python datata.py --command="verify_hash" --local="/Users/me/folder" --hash-file="/Users/me/Downloads/hash.txt"

  Command: list_commands
    List all the commands supported by the program
    Mandatory values: []
    Example: python datata.py --command="list_commands"

  Command: upload_files_to_s3
    Upload "prefix" folder inside "local" folder, to "bucket", with the same "prefix"; if "dry-run" is False. Otherwise just list the files that are going to be uploaded.
    Mandatory values: ['secret', 'key', 'bucket', 'local', 'dry-run']
    Example: python datata.py --command="upload_files_to_s3" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --dry-run="True"

  Command: set_s3_file_mime_type
    Add mime type to files in "bucket" (with "prefix"), based on file extension. List is in method "get_content_type_per_extension", in "helpers_files.py". Only files are changed if "dry-run" is False.
    Mandatory values: ['secret', 'key', 'bucket', 'dry-run']
    Example: python datata.py --command="set_s3_file_mime_type" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/" --dry-run="True"

  Command: list_local_folder
    List the folder content of "local" path.
    Mandatory values: ['local']
    Example: python datata.py --command="list_local_folder" --local="/Users/me/folder"

  Command: download_files_from_s3
    Download the "bucket" content (from "prefix") to "local" path, if "dry-run" is False. Otherwise just list the files that are going to be downloaded.
    Mandatory values: ['secret', 'key', 'bucket', 'local', 'dry-run']
    Example: python datata.py --command="download_files_from_s3" --key="AK..." --secret="07..." --bucket="mybucketname" --local="/Users/me/folder" --prefix="assets/images/" --dry-run="True"

  Command: list_server_folder
    List the server remote folder "serv-folder". It uses a ssh key "serv-key" or a server password "serv-pass" to connect to the server. If you want to use a password, then set "serv-key" to "/dev/null". If you want to use a SSH key, then set "serv-pass" to "".
    Mandatory values: ['serv-url', 'serv-user', 'serv-pass', 'serv-folder', 'serv-key']
    Example: python datata.py --command="list_server_folder" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"

  Command: download_files_from_server
    Download the files in remote server "serv-folder" to local folder "local" (if "dry-run" is False). It uses a ssh key "serv-key" or a server password "serv-pass" to connect to the server. If you want to use a password, then set "serv-key" to "/dev/null". If you want to use a SSH key, then set "serv-pass" to "".
    Mandatory values: ['serv-url', 'serv-user', 'serv-pass', 'serv-key', 'serv-folder', 'local', 'dry-run']
    Example: python datata.py --command="download_files_from_server" --serv-url="192.168.100.72" --serv-user="vagrant" --serv-pass="vagrant" --serv-key="/dev/null" --serv-folder="/var/www/wordpress/wp-content/themes/"  --local="/Users/me/folder" --dry-run="False"

  Command: list_s3_files
    List the content of the "bucket", starting from the "prefix".
    Mandatory values: ['secret', 'key', 'bucket']
    Example: python datata.py --command="list_s3_files" --key="AK..." --secret="07..." --bucket="mybucketname" --prefix="assets/images/"
```

## S3 bucket policy

The S3 bucket needs a policy like the next one, or more permissive, in order to work:

```json
 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Effect": "Allow",
             "Action": [
                 "s3:ListBucket"
             ],
             "Resource": [
                 "arn:aws:s3:::my-first-bucket",
                 "arn:aws:s3:::my-second-bucket"
             ]
         },
         {
             "Effect": "Allow",
             "Action": [
                 "s3:GetObject",
                 "s3:PutObject"
             ],
             "Resource": [
                 "arn:aws:s3:::my-first-bucket/*",
                 "arn:aws:s3:::my-second-bucket/*"
             ]
         }
     ]
 }
```



PYTHON 3 
virtualenv -p python3 venv
python3 -m pip install -r requirements.txt


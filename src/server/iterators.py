from .helpers import remote_item_is_file
from ..local.file import get_file_hash as get_local_file_hash

# File iterator
def files(settings, function_callback):
    iterate_over_files(settings, settings['serv-folder'], "", function_callback)

def fast_files(settings, function_callback):
    fast_iterator_over_files(settings, settings['serv-folder'], "", function_callback)

# Folder iterator
def folders(settings, function_callback):
    iterate_over_folders(settings, settings['serv-folder'], "", function_callback)

# This iterator list and calculates MD5 of all files in the folder (and subfolders) passed as parameter.
# If folder is /a, then it list all files /a/1.txt, /a/2.txt ... and files inside folders /a/b/1.txt, including MD5.
def fast_iterator_over_files(settings, rootPath, relativePath, functionCallback):
    remote_folder_path = "{}{}".format(rootPath,relativePath)
    # It will list all the files in current directory and subdirectories, returning file path and file MD5
    folderContent = settings['server_client'].execute("cd "+remote_folder_path+" && find -type f -exec md5sum '{}' +")
    for index, item in enumerate(folderContent):
        parts = item.split()
        # Path looks like "./antecesores.png", we need to remove first "./"
        file_relative_path = parts[1][2:].rstrip().encode('utf-8')
        parameters = {
            "server_file_md5": parts[0].rstrip().encode('utf-8'),
            "file_relative_path": file_relative_path,
            "full_server_path": "{}{}".format(settings['serv-folder'], file_relative_path)
        }
        if 'local' in settings:
            parameters["full_local_path"] = "{}{}".format(settings['local'], file_relative_path)
            parameters["local_file_md5"] = get_local_file_hash(parameters["full_local_path"])
        try:
            functionCallback(settings, parameters)
        except Exception, e:
            print ("\n------>ERROR with remote file '{}':".format(parameters))
            print (str(e))

# This iterator process file by file
def iterate_over_files(settings, rootPath, relativePath, functionCallback):
    remote_folder_path = "{}{}".format(rootPath,relativePath)
    folderContent = settings['server_client'].execute('ls '+remote_folder_path)
    #print ("Remote folder {} has items {}".format(remote_folder_path, len(folderContent)))
    for index, item in enumerate(folderContent):
        item = item.rstrip().encode('utf-8') #remove last line break
        item_path = "{}{}{}".format(rootPath,relativePath,item)
        if remote_item_is_file(settings['server_client'], item_path):
            try:
                functionCallback(settings, "{}{}".format(relativePath, item))
            except Exception, e:
                print ("\n------>ERROR with remote file '{}':".format(item_path))
                print (str(e))
        else:
            iterate_over_files(
                settings, 
                rootPath, # rootPath is always the same
                "{}{}/".format(relativePath,item), # relativePath is one level deeper
                functionCallback
            )

def iterate_over_folders(settings, rootPath, relativePath, functionCallback):
    remote_folder_path = "{}{}".format(rootPath,relativePath)
    folderContent = settings['server_client'].execute('ls -F '+remote_folder_path+' | grep /')
    #print "Remote folder {} has items {}".format(remote_folder_path, len(folderContent))
    for index, item in enumerate(folderContent):
        item = item.rstrip().encode('utf-8') #remove last line break
        item_path = "{}{}{}".format(rootPath,relativePath,item)
        functionCallback(settings, "{}{}".format(relativePath, item))
        iterate_over_folders(
            settings, 
            rootPath, # rootPath is always the same
            "{}{}".format(relativePath,item), # relativePath is one level deeper
            functionCallback
        )

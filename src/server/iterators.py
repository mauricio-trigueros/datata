from .helpers import remote_item_is_file

# File iterator
def files(settings, function_callback):
	iterate_over_files(settings, settings['serv-folder'], "", function_callback)

# Folder iterator
def folders(settings, function_callback):
	iterate_over_folders(settings, settings['serv-folder'], "", function_callback)


def iterate_over_files(settings, rootPath, relativePath, functionCallback):
	remote_folder_path = "{}{}".format(rootPath,relativePath)
	folderContent = settings['server_client'].execute('ls '+remote_folder_path)
	#print ("Remote folder {} has items {}".format(remote_folder_path, len(folderContent)))
	for index, item in enumerate(folderContent):
		item = item.rstrip() #remove last line break
		item_path = "{}{}{}".format(rootPath,relativePath,item)
		#print ("   Processing {}".format(item_path)),
		if remote_item_is_file(settings['server_client'], item_path):
			#print (" --is-a-file"),
			functionCallback(settings, "{}{}".format(relativePath, item))
		else:
			#print (" --is-a-folder")
			iterate_over_files(
				settings, 
				rootPath, # rootPath is always the same
				"{}{}/".format(relativePath,item), # relativePath is one level deeper
				functionCallback
			)

def iterate_over_folders(settings, rootPath, relativePath, functionCallback):
	remote_folder_path = "{}{}".format(rootPath,relativePath)
	folderContent = settings['server_client'].execute('ls '+remote_folder_path)
	#print "Remote folder {} has items {}".format(remote_folder_path, len(folderContent))
	for index, item in enumerate(folderContent):
		item = item.rstrip() #remove last line break
		item_path = "{}{}{}".format(rootPath,relativePath,item)
		#print "   Processing {}".format(item_path),
		if not remote_item_is_file(settings['server_client'], item_path):
			functionCallback(settings, "{}{}".format(relativePath, item))
			iterate_over_folders(
				settings, 
				rootPath, # rootPath is always the same
				"{}{}/".format(relativePath,item), # relativePath is one level deeper
				functionCallback
			)

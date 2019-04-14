import os
from src.mimes import is_image

# File iterator
def files(settings, function_callback):
    iterate_over_files(settings, settings['local'],settings['prefix'],function_callback)

# Folder iterator
def folders(settings, function_callback):
    iterate_over_folders(settings, settings['local'],settings['prefix'],function_callback)

# Images iterator
def images(settings, function_callback):
    iterate_over_images(settings, settings['local'],settings['prefix'],function_callback)

# Recursive function that executes function_callback with parameter file_path  against
# all the files in folder (and subfolders) set by parameter rootPath
# To execute function do_something (that takes one parameter filePath), we run it as:
# iterate_folder(settings, FOLDER, "", do_something)
# How to iterate the folders: if rootPath is /var/root/, this rootPath is always the same, we increase
# relativePath to be folderOne/, folderOne/insideOne/, ...
def iterate_over_files(settings, rootPath,relativePath,functionCallback):
    # We need to concatenate the path to explore, both rootPath and relativePath ends with "/"
    print("{}{}".format(rootPath,relativePath))
    folderContent = os.listdir("{}{}".format(rootPath,relativePath))
    for item in folderContent:
        # item is a folder name (without "/") or a file name
        # we calculate the absolute path of the item, and check if it is file or folder
        item_path = "{}{}{}".format(rootPath,relativePath,item)
        if os.path.isdir(item_path):
            # if item is a folder, we need to itereate again the function
            iterate_over_files(
                settings,
                rootPath, # rootPath is always the same
                "{}{}/".format(relativePath,item), # relativePath is one level deeper
                functionCallback
            )
        else:
            # if item is not a folder, we assume that is a file. 
            # item_path is the full path to the file (like /home/banana/project/myfile.png)
            # but we need to send just the relative path, as we do with S3 listing, so that is project/myfile.png
            functionCallback(settings, "{}{}".format(relativePath, item))

# Copy paste of iterate_over_files
# Refactor it!!
def iterate_over_images(settings, rootPath,relativePath,functionCallback):
    # We need to concatenate the path to explore, both rootPath and relativePath ends with "/"
    folderContent = os.listdir("{}{}".format(rootPath,relativePath))
    for item in folderContent:
        # item is a folder name (without "/") or a file name
        # we calculate the absolute path of the item, and check if it is file or folder
        item_path = "{}{}{}".format(rootPath,relativePath,item)
        if os.path.isdir(item_path):
            # if item is a folder, we need to itereate again the function
            iterate_over_files(
                settings,
                rootPath, # rootPath is always the same
                "{}{}/".format(relativePath,item), # relativePath is one level deeper
                functionCallback
            )
        else:
            # if item is not a folder, we assume that is a file. 
            # item_path is the full path to the file (like /home/banana/project/myfile.png)
            # but we need to send just the relative path, as we do with S3 listing, so that is project/myfile.png
            # Because we are iterating images, we need to check that file is an image
            if is_image(item):
                functionCallback(settings, "{}{}".format(relativePath, item))

# Iterate and executes the function callback against Folders
def iterate_over_folders(settings, rootPath,relativePath,functionCallback):
    # We need to concatenate the path to explore, both rootPath and relativePath ends with "/"
    folderContent = os.listdir("{}{}".format(rootPath,relativePath))
    for item in folderContent:
        # item is a folder name (without "/") or a file name
        # we calculate the absolute path of the item, and check if it is file or folder
        item_path = "{}{}{}".format(rootPath,relativePath,item)
        if os.path.isdir(item_path):
            # Execute callback and continue
            #functionCallback(settings, item_path)
            functionCallback(settings, "{}{}".format(relativePath, item))
            iterate_over_folders(
                settings,
                rootPath, # rootPath is always the same
                "{}{}/".format(relativePath,item), # relativePath is one level deeper
                functionCallback
            )

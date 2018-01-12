import os
from .file import local_file_exist, get_file_size

def execute_command_according_strategy(command, settings, destination_file, original_file):
	if not command:
		print ("--no-command")
		return

	print ("--compressing"),

	# Execute previous instructions, depending on strategy
	if settings['strategy'] == 'overwrite':
		print ("--overwritting"),
		# We need to remove destination file first
		if os.path.isfile(destination_file):
			os.remove(destination_file),
			print ("--prev-file-removed"),
	elif settings['strategy'] == 'skip-if-exist':
		# If file exist, do nothing
		if os.path.isfile(destination_file):
			print ("--prev-file-exist")
			return
	else:
		sys.exit("Strategy  '{}' not found".format(settings['strategy']))

	# Execute command
	os.system(command)

	# Now we need to check if the file has been generated, if we have a valid output
	# otherwise we will need to copy the file manually
	if (local_file_exist(destination_file)) and (int(get_file_size(destination_file)) > 0) :
		print ("--executed"),
	else:
		print ("--copying-original-file")
		os.system("cp {} {}".format(original_file, destination_file))
		return

	# Now we show the result of the operation
	reduction = int ((float (get_file_size(destination_file)) / float (get_file_size(original_file))) * 100)
	print ("--result-size-{}%".format(reduction))

	if settings['delete-after']:
		print ("--deleting-original")
		os.remove(original_file)

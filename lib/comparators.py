
# Compare 2 dict with file info
# for example, output of server_md5_files_iterator and local_md5_files_iterator)
# Iterates dictA, and returns dicts that are NOT in dictB (or has different md5)
def compare_file_dicts(dictA, dictB):
	diffs = []
	for fil in dictA:
		print(" Checking {}...".format(fil), end=' ')
		remote = dictB.get(fil)
		if not remote:
			print('--NOT-FOUND')
			diffs.append(dictA[fil])
		else:
			print('--in-remote', end=' ')
			if dictA[fil]['md5'] == remote['md5']:
				print('--same-md5')
			else:
				print('--DIFFERENT-MD5')
				remote = dictB.get(fil)
				diffs.append(dictA[fil])
	return diffs
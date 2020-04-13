
# Compare 2 dict with file info
# for example, output of server_md5_files_iterator and local_md5_files_iterator)
# Iterates dictA, and returns dicts that are NOT in dictB (or has different md5)
def compare_file_dicts(dictA, dictB, md5=True, verbose=True):
	diffs = []
	for fil in dictA:
		if verbose: print(" Checking {}...".format(fil), end=' ')
		remote = dictB.get(fil)
		if not remote:
			if verbose: print('--NOT-FOUND')
			diffs.append(dictA[fil])
		else:
			if verbose: print('--found', end=' ')
			# We may want to compare MD5
			if md5:
				if dictA[fil]['md5'] == remote['md5']:
					if verbose: print('--same-md5')
				else:
					if verbose: print('--DIFFERENT-MD5')
					remote = dictB.get(fil)
					diffs.append(dictA[fil])
			else:
				if verbose: print('--no-md5-check')
	print("TOTAL: {}".format(len(diffs)))
	return diffs
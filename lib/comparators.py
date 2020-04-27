
# Compare 2 dict with file info
# for example, output of server_md5_files_iterator and local_md5_files_iterator)
# Iterates dictA, and returns dicts that are NOT in dictB (or has different md5)
# Files that are in dictA but not in dictB 
def compare_file_dicts(dictA, dictB, verbose=True):
	diffs = []
	for fil in dictA:
		if verbose: print(" Checking {}...".format(fil), end=' ')
		remote = dictB.get(fil)
		if not remote:
			if verbose: print('--NOT-FOUND')
			diffs.append(dictA[fil])
		else:
			if dictA[fil].get_md5() == remote.get_md5():
				if verbose: print('--same-md5')
			else:
				if verbose: print('--DIFFERENT-MD5')
				remote = dictB.get(fil)
				diffs.append(dictA[fil])
	return diffs



# Return iles that are in dictA but not in dictB.
def compare_only_missing(dictA, dictB, verbose=True):
	diffs = []
	for fil in dictA:
		if verbose: print(" Checking '{}'...".format(fil), end=' ')
		if not dictB.get(fil):
			if verbose: print('--not-found')
			diffs.append(dictA[fil])
		else:
			if verbose: print('--found')
	return diffs

# Files that are in dictA and dictB, but with different MD5.
def compare_only_different(dictA, dictB, verbose=True):
	diffs = []
	for fil in dictA:
		if verbose: print(" Checking {}...".format(fil), end=' ')
		remote = dictB.get(fil)
		if remote and dictA[fil].get_md5() != remote.get_md5():
			if verbose: print('--DIFFERENT-MD5')
			diffs.append(dictA[fil])
	return diffs
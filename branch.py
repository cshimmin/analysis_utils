import ROOT as r
import re

def match_branches_from_file(selection_files, tree):
	# load regular expression from file
	if not type(selection_files) == list:
		selection_files = [selection_files]
	
	selections = []
	for f in selection_files:
		selections.extend(open(f).readlines())
	return match_branches(selections, tree)
	
def match_branches(selections, tree):
	if not type(selections) == list:
		selections = [selections]

	regexes = []
	for line in selections:
		line = line.strip() # ditch whitespace (regex should use $^ delims if necessary)
		if line == '' or line.startswith('#'):
			continue	# ditch blank lines and comments
		regexs.append(re.compile(line))
	
	all_branches = [b.GetName() for b in tree.GetListOfBranches()]

	# keep only branches that match at least one of the selection strings
	matched_branches = filter(lambda b: any((regex.match(b)!=None for regex in regexs)), all_branches)
	return matched_branches


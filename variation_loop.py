#!/usr/bin/env python

import variation

def run(input_tree, nominal=None, variations=[]):
	# make sure that nominal is included in the full list
	if nominal and not nominal in variations:
		variations.append(nominal)

	# set the fallback reference for all the variations.
	for v in variations:
		v.set_fallback(nominal if nominal else input_tree)

	# set the fallback for nominal to be just the ttree
	if nominal:
		nominal.set_fallback(input_tree)
	
	variations_and_functions = [(v, v.process_fn) for v in variations]

	if len(variations) == 0:
		print "Warning! No variations to process. Aborting..."
		return
	
	total_entries = input_tree.GetEntries()
	for i,evt in enumerate(input_tree):
		if i%1000==0:
			print "Processing %d/%d ~ %.2f%%" % (i, total_entries, 100.*i/total_entries)

		keep = False
		for v,p in variations_and_functions:
			try:
				v.reset()
				p(v)
				v.set_valid(True)
				keep = True
			except variation.SkipEvent:
				# just move on to the next one!
				pass

		if keep:
			# if any of the variations managed to pass, write out everything.
			for v in variations:
				v.write_ntuple()

if __name__ == "__main__":
	pass


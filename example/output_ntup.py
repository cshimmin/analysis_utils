#!/usr/bin/env python

'''
 Example program demonstrating the use of the
 pytree module to easily create output ntuples,
 with practically zero ROOT-boilerplate crap!
'''

from analysis_utils.pytree import PyTree
import ROOT as r
import numpy as np

if __name__ == "__main__":
	outfile = r.TFile('output_ntuple.root', 'recreate')

	ntup = PyTree('example', 'example')

	for i in xrange(5000):
		# call reset on the PyTree; this will set all the 
		# sclars to 0, and clear out any vector-valued
		# branches.
		ntup.reset()

		# calculate some silly variables at random
		uniform1 = np.random.rand()
		uniform50 = np.random.rand()*50.
		gauss = np.random.normal(0,1)

		rlength = int(np.random.gamma(1, 5))
		rvector_gamma2 = np.random.gamma(2, 25e3, rlength)
		rvector_gamma3 = np.random.gamma(3, 15e3, rlength)

		# now write them out. note that the branches
		# are created on the fly as needed.
		ntup.write_branch(i, 'event_number', int)
		ntup.write_branch(uniform1, 'uniform1', float)
		ntup.write_branch(uniform50, 'uniform50', int)
		ntup.write_branch(gauss, 'gauss', float)
		ntup.write_branch(rvector_gamma2, 'rvector_gamma2', [float])
		ntup.write_branch(rvector_gamma3, 'rvector_gamma3', [float])
		ntup.write_branch(rlength, 'rvector_n', int)

		# For illustration, write one branch out later
		# than the others. This branch will be
		# backfilled with 0's for the first 20 events.
		# Then it should be identical to `event_number`
		if i>20:
			ntup.write_branch(i, 'late_branch', int)

		# call fill to commit the current row to file
		ntup.Fill()
	
	outfile.Write()


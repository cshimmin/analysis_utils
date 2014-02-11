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
    # create an output file
    outfile = r.TFile('ntuple.root', 'recreate')

    ntup = PyTree('example', 'example', verbose=True)

    print "Generating output..."
    N_EVENTS = 5000
    for i in xrange(N_EVENTS):
        if i%1000 == 0:
            print "  %d/%d events ~ %.2f%%" % (i, N_EVENTS, 100.*i/N_EVENTS)
        # call reset on the PyTree; this will set all the
        # sclars to 0, and clear out any vector-valued
        # branches.
        ntup.reset()

        # calculate some silly variables at random
        uniform = np.random.rand()
        gauss = np.random.normal(0, 5)

        rlength = int(np.random.gamma(1, 5))
        rvector_gamma2 = np.random.gamma(2, 25e3, rlength)
        rvector_gamma3 = np.random.gamma(3, 15e3, rlength)

        # now write them out. note that the branches
        # are created on the fly as needed.
        # note that type specifiers are optional, but
        # are generally a good idea given python's loose
        # typesystem.
        ntup.write_branch(i, 'event_number')
        ntup.write_branch(uniform, 'uniform')
        ntup.write_branch(gauss, 'gauss', float)
        ntup.write_branch(rlength, 'rvector_n', int)
        ntup.write_branch(rvector_gamma2, 'rvector_gamma2')
        ntup.write_branch(rvector_gamma3, 'rvector_gamma3', [float])

        # For illustration, write one branch out later
        # than the others. This branch will be
        # backfilled with 0's for the first 20 events.
        # Then it should be identical to `event_number`
        if i > 20:
            ntup.write_branch(i, 'late_branch', int)

        # call fill to commit the current row to file
        ntup.Fill()

    outfile.Write()
    print "Done! Saved to file %s" % outfile.GetName()

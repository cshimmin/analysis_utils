#!/usr/bin/env python

import argparse
import analysis_utils.variation as variation
from analysis_utils.variation_loop import run

import ROOT as r

##########################
## Misc utility methods ##
##########################

''' simple function to implement crude MET (2d vector) smearing '''


def smear_met(et, phi, width):
    from numpy import cos, sin
    from numpy.random import normal
    from numpy.linalg import norm
    x = et * cos(phi) + normal(0, width)
    y = et * sin(phi) + normal(0, width)
    return norm([x, y])

''' here are some ugly globals to keep track of
    the calculation statistics; this is for illustration
    purposes only, and wouldn't be necessary for a typical
    analysis. '''
calc_stats = {}


def report_calculation(name):
    try:
        calc_stats[name] += 1
    except KeyError:
        calc_stats[name] = 1


def print_stats():
    for n, c in calc_stats.items():
        print "%s:\t%d" % (n, c)


###################################################
## AnalysisVariation class (defines calculables) ##
###################################################
class ExampleVariation(variation.AnalysisVariation):

    def __init__(self, *args, **kwargs):
        variation.AnalysisVariation.__init__(self, *args, **kwargs)
        # capture the (optional) systematics parameters
        self._mu_shift = kwargs.get('mu_shift', 0)
        self._met_width = kwargs.get('met_width', 0)

    ##########################
    ## Calculable functions ##
    ##########################

    ''' Get the number of muons in the D3PD '''

    def _get_n_muons(self):
        self.defer()
        report_calculation('n_muons')
        return self.mu_n

    ''' Get the number of muons w/ pt>65GeV.
	    Subject to the mu_shift systematic '''

    def _get_n_hard_muons(self):
        self.defer_unless(self._mu_shift > 0)
        report_calculation('n_hard_muons')
        return sum([(mpt + self._mu_shift) > 65 for mpt in self.mu_pt])

    ''' Get the number of jets in the D3PD '''

    def _get_n_jets(self):
        self.defer()
        report_calculation('n_jets')
        return self.jet_n

    ''' Get the smeared MET (random MET added to D3PD value)
	    Subject to the met_width parameter '''

    def _get_met_smeared(self):
        if self._met_width == 0:
            self.defer()
            report_calculation('met_smeared')
            return self.met_et

        # calculate MET with some random smearing
        report_calculation('met_smeared')
        return smear_met(self.met_et, self.met_et, self._met_width)


#############################
## Cutflow implementations ##
#############################
''' A very basic (if not very meaningful) analysis cutflow '''


def analysis_cutflow(v):
    v.cut_if(v.n_muons < 2, "2muons")
    v.cut_if(v.n_hard_muons < 1, "hardmu")
    v.cut_if(v.met_smeared < 80, "met80")

''' A control region cutflow, that implements the basic cutflow
    above, and additionally requires a bunch of jets '''


def jetCR_cutflow(v):
    analysis_cutflow(v)

    v.cut_if(v.n_jets < 3, "3jets")


#########################
## Main program driver ##
#########################
if __name__ == "__main__":
    parser = argparse.ArgumentParser("test variational analysis")
    parser.add_argument('--tree', default='physics',
                        help='the input TTree name')
    parser.add_argument('input_file', nargs='+',
                        help='the input file(s) to use')
    args = parser.parse_args()

    # load up the input files
    input_tree = r.TChain(args.tree)
    map(input_tree.Add, args.input_file)

    # set up the variations to be run
    var_nominal = ExampleVariation(process_fn=analysis_cutflow,
                                   name="nominal")

    variations_to_run = [
        ExampleVariation(process_fn=analysis_cutflow,
                         name='shift muon pt', mu_shift=25),
        ExampleVariation(process_fn=analysis_cutflow,
                         name='smeared met', met_width=20),
        ExampleVariation(process_fn=jetCR_cutflow,
                         name='jets CR'),
    ]

    # run the analysis using the variation_loop driver:
    run(input_tree, nominal=var_nominal, variations=variations_to_run)

    # print the results
    print "OKAY Done!"
    print
    for v in variations_to_run:
        print "==== Cutflow: %s ====" % v.name
        print v.cutflow
        print
    print ">>>> Calculation stats: <<<<"
    print_stats()
    print

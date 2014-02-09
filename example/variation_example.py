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
	x = et * cos(phi) + normal(0,width)
	y = et * sin(phi) + normal(0,width)
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
	for n,c in calc_stats.items():
		print "%s:\t%d" % (n,c)



###################################################
## AnalysisVariation class (defines calculables) ##
###################################################

class ExampleVariation(variation.AnalysisVariation):
	def __init__(self, *args, **kwargs):
		variation.AnalysisVariation.__init__(self, *args, **kwargs)
		# capture the (optional) systematics parameters
		self.mu_shift = kwargs.get('mu_shift', 0)
		self.met_width = kwargs.get('met_width', 0)
	
	##########################
	## Calculable functions ##
	##########################
	
	''' Get the number of muons in the D3PD '''
	def _get_n_muons(self):
		self.defer()
		report_calculation('n_muons')
		return self.mu_staco_pt.size()

	''' Get the number of muons w/ pt>80GeV.
	    Subject to the mu_shift systematic '''
	def _get_n_hard_muons(self):
		self.defer_unless( self.mu_shift > 0 )
		if self.name == 'jets CR':
			print "why am i calc'ing?"
		report_calculation('n_hard_muons')
		return sum([(mpt + self.mu_shift) > 80e3 for mpt in self.mu_staco_pt])

	''' Get the number of jets in the D3PD '''
	def _get_n_jets(self):
		self.defer()
		report_calculation('n_jets')
		return self.jet_AntiKt4LCTopo_pt.size()

	''' Get the (possibly smeared) MET from the D3PD.
	    Subject to the met_width parameter '''
	def _get_met(self):
		if self.met_width == 0:
			self.defer()
			report_calculation('met')
			return self.MET_RefFinal_et

		# calculate MET with some random smearing
		report_calculation('met')
		return smear_met(self.MET_RefFinal_et, self.MET_RefFinal_phi, self.met_width)




#############################
## Cutflow implementations ##
#############################

''' A very basic (if not very meaningful) analysis cutflow '''
def analysis_cutflow(v):
	v.cut_if(v.n_muons < 3, "3muons")
	v.cut_if(v.n_hard_muons < 1, "hardmu")
	v.cut_if(v.met < 50e3, "met50")

''' A control region cutflow, that implements the basic cutflow
    above, and additionally requires a bunch of jets '''
def jetCR_cutflow(v):
	analysis_cutflow(v)

	v.cut_if(v.n_jets < 20, "20jets")




#########################
## Main program driver ##
#########################

if __name__ == "__main__":
	parser = argparse.ArgumentParser("test variational analysis")
	parser.add_argument('--tree', default='susy', help='the input TTree name')
	parser.add_argument('input_file', nargs='+', help='the input file(s) to use')
	args = parser.parse_args()

	# load up the input files
	input_tree = r.TChain(args.tree)
	map(input_tree.Add, args.input_file)


	# set up the variations to be run
	var_nominal = ExampleVariation(process_fn=analysis_cutflow,
			name="nominal")

	variations_to_run = [
		ExampleVariation(process_fn=analysis_cutflow,
			name='shift muon pt', mu_shift=25e3),
		ExampleVariation(process_fn=analysis_cutflow,
			name='smeared met', met_width=20e3),
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

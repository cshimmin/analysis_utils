#!/usr/bin/env python

import argparse
import analysis_utils.variation as variation
from analysis_utils.variation_loop import run

import ROOT as r

class ExampleVariation(variation.AnalysisVariation):
	def __init__(self, *args, **kwargs):
		variation.AnalysisVariation.__init__(self, *args, **kwargs)

		self.mu_factor = 0
	
	def _get_n_muons(self):
		return self.mu_staco_pt.size()
	def _get_n_hard_muons(self):
		mu_factor = self.mu_factor
		return sum([(mpt + mu_factor) > 80e3 for mpt in self.mu_staco_pt])
	def _get_n_jets(self):
		return self.jet_AntiKt4LCTopo_pt.size()

def process(v):
	v.cut_if(v.n_muons < 3, "3mu")
	v.cut_if(v.n_hard_muons < 1, "hardmu")
	v.cut_if(v.n_jets < 20, "20jets")

	print "Accpted event in variation `%s`! EventNumber = %s" % (v.name, v.EventNumber)

if __name__ == "__main__":
	parser = argparse.ArgumentParser("test variational analysis")

	parser.add_argument('--tree', default='susy', help='the input TTree name')
	parser.add_argument('input_file', nargs='+', help='the input file(s) to use')

	args = parser.parse_args()

	# load up the input files
	input_tree = r.TChain(args.tree)
	map(input_tree.Add, args.input_file)

	# set up our variations to be run
	var_nominal = ExampleVariation(process_fn=process, name='nominal')

	var_shift_muon_pt = ExampleVariation(process_fn=process, name='shift muon pt')
	var_shift_muon_pt.mu_factor = 25e3

	variations_to_run = [var_nominal, var_shift_muon_pt]

	run(input_tree, nominal=var_nominal, variations=variations_to_run)

	print "OKAY Done!"
	print

	for v in variations_to_run:
		print "==== Cutflow: %s ====" % v.name
		print v.cutflow
		print

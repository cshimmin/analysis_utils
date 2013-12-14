#!/usr/bin/env python

import os
import ROOT as r

'''
This utility sets up a ROOT-accessible (cint) function to look up
montecarlo weights given a unique dataset identifer.

Before using the utility, it must be initialized:
	init_lumi_weights(xs_file='crosssections.txt', counts_file='counts.txt', lumi_scale=20.3e3)

Then, you may use the get_lumi_weight in ROOT, for example, when drawing distributions:
	# here, the TTree has a branch called mc_dataset_id which corresponds to the unique DSID
	some_tree.Draw('var1', 'get_lumi_weight(mc_dataset_id) * (some || other || selection)')

The expected format for the cross section file is whitespace-delimited and each line should contain:
	# comments are ignored:
	<dsid>	<logical name (no whitespace)>	<cross-section>	<k-factor>	<filter efficiency>

The expected format for the counts file is:
	<dsid>	<number of events in sample>	<summed weights of events in sample>

Note that the lumi_scale passed to init_lumi_weights() should have the (inverse) same units as
cross-sections in the xs file.
'''

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
r.gROOT.ProcessLine('.L %s' % os.path.join(THIS_PATH, 'weights.C+'))

def parse_xs_file(xs_file):
	# xs file should be formatted as:
	# dsid	physname	xs(pb)	kfactor	filt.eff
	xs_info = {}
	for l in open(xs_file).readlines():
		l = l.strip()
		if l == '' or l.startswith('#'): continue
		fields = l.split()
		dsid = int(fields[0])
		xs = float(fields[2])
		kfac = float(fields[3])
		filt = float(fields[4])
		xs_info[dsid] = {'xs': xs, 'kfac': kfac, 'filter':filt}
	return xs_info

def parse_counts_file(counts_file):
	# counts file should be formatted as:
	# dsid	nevt	nevt_wt
	counts_info = {}
	for l in open(counts_file).readlines():
		l = l.strip()
		if l == '' or l.startswith('#'): continue
		fields = l.split()
		dsid = int(fields[0])
		nevt = int(fields[1])
		nevt_wt = float(fields[2])
		counts_info[dsid] = {'nevt': nevt, 'nevt_wt': nevt_wt}
	return counts_info

def init_lumi_weights(xs_file, counts_file, lumi_scale=1.0):
	r.clear_lumi_weights()
	r.set_lumi_scale(lumi_scale)

	xs_info = parse_xs_file(xs_file)
	counts_info = parse_counts_file(counts_file)

	# get a list of DSID's which are defined in both files.
	dsid_defined = set(xs_info.keys()).intersection(counts_info.keys())

	for dsid in dsid_defined:
		c = counts_info[dsid]
		x = xs_info[dsid]
		lumi_weight = x['xs'] * x['kfac'] * x['filter']/ c['nevt_wt']

		r.set_lumi_weight(dsid, lumi_weight)


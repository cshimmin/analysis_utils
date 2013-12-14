#!/usr/bin/env python

import argparse
import ROOT as r

from analysis_utils.generic_object import get_objects

class SkipEvent(Exception):
	def __init__(self, reason):
		self.reason = reason

particle_mass = { 'el': 0, 'mu': 0.105, 'z': 91.188 }	# masses in GeV

def set_4vector(p):
	p.v4 = r.TLorentzVector()
	p.v4.SetPtEtaPhiM(p.pt, p.eta, p.phi, particle_mass[p.prefix])

def process(t):
	electrons = get_objects(t, 'el')
	muons = get_objects(t, 'mu')
	jets = get_objects(t, 'jet')

	# veto any jet harder than 15GeV
	hard_jets = filter(lambda j: j.pt>15, jets)
	if len(hard_jets) != 0:
		raise SkipEvent('jetveto')

	# require at least 2 electrons or 2 muons
	if len(electrons) < 2 and len(muons) < 2:
		raise SkipEvent('2lepton')

	leptons = electrons + muons

	# veto a third lepton
	if not len(leptons) == 2:
		raise SkipEvent('3lepton')
	
	# require the leptons have opposite charge
	if not leptons[0].charge * leptons[1].charge < 1:
		raise SkipEvent('charge')

	# build 4-vectors for the leptons and reconstruct their sum:
	map(set_4vector, leptons)

	z_boson = leptons[0].v4 + leptons[1].v4

	# require the reconstructed mass is within 15 GeV of the z-mass
	if not abs(z_boson.M() - particle_mass['z']) < 15:
		raise SkipEvent('zmass')
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser('very basic example of Z-boson event reconstruction')

	parser.add_argument('input_file', nargs='+', help='the input file(s)')

	args = parser.parse_args()

	# load in the input files:
	t = r.TChain('physics')
	map(t.Add, args.input_file)

	# keep track of why events fail:
	total_events = t.GetEntries()
	fails = {}
	passed = 0
	for i,evt in enumerate(t):
		if i%1000==0:
			print "%d/%d ~ %0.2f%%" % (i, total_events, 100.*i/total_events)
		try:
			process(evt)
		except SkipEvent as e:
			if not e.reason in fails:
				fails[e.reason] = 0
			fails[e.reason] += 1

		# if we made it this far, we are accepting the event.
		# you might want to call Fill() on a TTree or histogram here.
	
	print "failed events:"
	for reason, evts in fails.items():
		print "  %s:\t%d" % (reason, evts)


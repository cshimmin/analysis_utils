#!/usr/bin/env python

import ROOT as r
# ask root not to hijack command-line args
r.PyConfig.IgnoreCommandLineOptions = True

from analysis_utils.variation_loop import run
from analysis_utils.variation import AnalysisVariation
from analysis_utils.root.dpd_object import fetch_objects, build_tlv, tlv_particle, met_object
from analysis_utils.root.pytree import PyTree

class ExampleAnalysis(AnalysisVariation):
    def __init__(self, *args, **kwargs):
        # You should hand the arguments to AnalysisVariation.
        AnalysisVariation.__init__(self, *args, **kwargs)

        # if you want to capture additional arguments, you
        # can get them from kwargs here. E.g.:
        self._some_argument = kwargs.get('some_argument', None)

        # create a PyTree for the output ntuple
        self._output_tree = PyTree('example', 'example')

    ##########################
    ## Calculable functions ##
    ##########################

    ''' Get electron objects from the D3PD. Note that we also
        construct a TLorentzVector for each object. '''
    def _get_all_electrons(self):
        return [build_tlv(el, mass=0) for el in fetch_objects(self._source, 'el')]

    def _get_nonoverlap_electrons(self):
        return filter( lambda el: not any(
            (el.tlv.DeltaR(ph.tlv) < 0.2 for ph in self.all_photons) ),
            self.all_electrons )

    def _get_hard_electrons(self):
        return filter(lambda el: el.pt > 45, self.nonoverlap_electrons)

    def _get_all_photons(self):
        return [build_tlv(ph, mass=0) for ph in fetch_objects(self._source, 'ph')]

    def _get_all_jets(self):
        return map(build_tlv, fetch_objects(self._source, 'jet'))

    def _get_nonoverlap_jets(self):
        return filter( lambda j: not any(
            (j.tlv.DeltaR(el.tlv) < 0.1 for el in self.hard_electrons) ),
            self.all_jets)
    
    def _get_z_boson(self):
        electrons = self.hard_electrons
        if len(electrons) < 2:
            raise CalculationError('require two electrons to reconstruct Z')
        el1, el2 = electrons[:2]

        return tlv_particle(el1.tlv + el2.tlv)
    
    def _get_met(self):
        return met_object(et=self.met_et, phi=self.met_phi)

    def _get_delta_phi(self):
        from numpy import pi
        return abs(pi - abs(pi - abs(self.met.phi - self.z_boson.phi)))


    ###################
    ## Output ntuple ##
    ###################

    ''' override reset() so we can also clear the output ntuple
        on each new entry '''
    def reset(self):
        AnalysisVariation.reset(self)
        # make sure to reset the output tree
        self._output_tree.reset()

    ''' This gets called for each event that made it all
        the way through process_entry() without failing a cut.
        So, we should populate our ntuple and call Fill(). '''
    def accept_entry(self):
        t = self._output_tree

        # we can write out basic scalar branches:
        t.write_branch(self.event_number, 'event_number')
        t.write_branch(self.delta_phi, 'delta_phi')

        # we can write certain attributes from simple objects:
        t.write_object(self.met, 'met', ['et','phi','x','y'])
        t.write_object(self.z_boson, 'z', ['pt','eta','phi','m'])

        # and we can even write out collections of objects:
        t.write_object(self.hard_electrons, 'el', ['pt','eta','phi','charge'])
        t.write_object(self.nonoverlap_jets, 'jet', ['pt','eta','phi','m'])

        # make sure to call Fill() to commit the entry to file.
        t.Fill()

def process_entry(v):
    v.cut_if( len(v.all_electrons) < 2,
            '2el' )
    v.cut_if( len(v.nonoverlap_electrons) < 2,
            '2el (nonoverlap)' )
    v.cut_if( len(v.hard_electrons) < 2,
            '2el (hard)' )

    z_mass = v.z_boson.m
    v.cut_if( z_mass < 76 or z_mass > 106,
            'z_mass +/- 15' )
    v.cut_if( v.delta_phi < 2.8,
            'delta_phi' )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Example analysis using calculables")
    parser.add_argument("--tree", default="physics", help="The input TTree name")
    parser.add_argument("--out", default="calculated.root", help="The output filename")
    parser.add_argument("input_file", nargs="+", help="The input root file(s)")
    args = parser.parse_args()

    # load up the input file(s)
    input_tree = r.TChain(args.tree)
    map(input_tree.Add, args.input_file)

    # create the output file. Note that this should be done before
    # creating the ExampleAnalysis instance, so that the TTree will
    # have the correct output context.
    outfile = r.TFile(args.out, 'recreate')

    nominal = ExampleAnalysis(process_fn=process_entry, name="example")

    # run the analysis using the variaton_loop driver (with only
    # the nominal "variation".
    run(input_tree, nominal=nominal)

    outfile.Write()
    outfile.Close()

    print "==== Cutflow ===="
    print nominal._cutflow

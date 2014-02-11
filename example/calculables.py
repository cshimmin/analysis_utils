#!/usr/bin/env python

import ROOT as r
# ask root not to hijack command-line args
r.PyConfig.IgnoreCommandLineOptions = True

from analysis_utils.variation_loop import run
from analysis_utils.variation import AnalysisVariation
from analysis_utils.generic_object import fetch_objects, build_tlv, tlv_particle

class ExampleAnalysis(AnalysisVariation):
    def __init__(self, *args, **kwargs):
        # You should hand the arguments to AnalysisVariation.
        AnalysisVariation.__init__(self, *args, **kwargs)

        # if you want to capture additional arguments, you
        # can get them from kwargs here. E.g.:
        self._some_argument = kwargs.get('some_argument', None)

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
    
    def _get_z_boson(self):
        electrons = self.hard_electrons
        if len(electrons) < 2:
            raise CalculationError('require two electrons to reconstruct Z')
        el1, el2 = electrons[:2]

        return tlv_particle(el1.tlv + el2.tlv)

    def _get_delta_phi(self):
        from numpy import pi
        return abs(pi - abs(pi - abs(self.met_phi - self.z_boson.phi)))

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

    nominal = ExampleAnalysis(process_fn=process_entry, name="example")

    # run the analysis using the variaton_loop driver (with only
    # the nominal "variation".
    run(input_tree, nominal=nominal, entry_limit=100)

    print "==== Cutflow ===="
    print nominal._cutflow

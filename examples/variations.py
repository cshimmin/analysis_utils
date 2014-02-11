#!/usr/bin/env python

import ROOT as r
# ask ROOT not to hijack command-line args
r.PyConfig.IgnoreCommandLineOptions = True

import analysis_utils.variation as variation
from analysis_utils.variation_loop import run
from analysis_utils.root.pytree import PyTree
from analysis_utils.root.dpd_object import get_objects, tlv_particle, met_object


##########################
## Misc utility methods ##
##########################

''' simple function to implement crude MET (2d vector) smearing '''
def smear_met(et, phi, width):
    from numpy import cos, sin, arctan, pi
    from numpy.random import normal
    from numpy.linalg import norm
    x = et * cos(phi) + normal(0, width)
    y = et * sin(phi) + normal(0, width)
    phi = arctan(y / x) + (x<0) * pi * (-1 if y<0 else 1)
    return norm([x, y]), phi


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


##############################################################
## AnalysisVariation class (defines calculables and output) ##
##############################################################
class ExampleVariation(variation.AnalysisVariation):

    def __init__(self, *args, **kwargs):
        variation.AnalysisVariation.__init__(self, *args, **kwargs)
        # create an output tree, if requested
        try:
            output_name = kwargs['output_name']
        except KeyError:
            # if no output name supplied, use the descriptive
            # name (with whitespace replaced by underscores
            output_name = '_'.join(self._name.split())
        self._output_tree = PyTree(output_name, self._name)

        # capture the (optional) systematics parameters
        self._mu_width = kwargs.get('mu_width', 0)
        self._met_width = kwargs.get('met_width', 0)

    def reset(self):
        variation.AnalysisVariation.reset(self)
        # make sure to reset the output tree
        self._output_tree.reset()

    ##########################
    ## Calculable functions ##
    ##########################

    ''' Get muon objects from the D3PD '''
    def _get_all_muons(self):
        from numpy.random import normal
        self.defer_unless( self._mu_width > 0 )
        report_calculation('all_muons')
        muons = get_objects(self._source, 'mu')

        if self._mu_width > 0:
            # smear the muon pT randomly
            from numpy.random import normal
            for mu in muons:
                mu.pt += mu.pt * normal(0, self._mu_width)

        return muons
    
    ''' Get muons w/ pt>45GeV.
        Subject to the mu_width systematic '''
    def _get_hard_muons(self):
        # defer to the nominal variation, unless were's shifting
        # the muons definition.
        self.defer_unless( self._mu_width > 0 )
        report_calculation('hard_muons')
        shift = self._mu_width
        return filter( lambda mu:
                (mu.pt + shift) > 45,
            self.all_muons )

    ''' Get jet objects from the D3PD '''
    def _get_all_jets(self):
        self.defer()
        report_calculation('all_jets')
        return get_objects(self._source, 'jet')

    ''' Get the smeared MET (random MET added to D3PD value)
        Subject to the met_width parameter '''
    def _get_met_smeared(self):
        if self._met_width == 0:
            self.defer()
            report_calculation('met_smeared')
            return met_object(self.met_et, self.met_phi)

        # calculate MET with some random smearing
        report_calculation('met_smeared')
        return met_object(*smear_met(self.met_et, self.met_phi, self._met_width))
    
    ''' Try to build a Z boson by adding the 4-vectors of
        two hard muons. Otherwise return None '''
    def _get_z_boson(self):
        self.defer_unless( self._mu_width > 0 )
        report_calculation('z_boson')

        muons = self.hard_muons
        if len(muons) < 2:
            return None
        
        z_vector = r.TLorentzVector()
        for m in muons[:2]:
            tlv = r.TLorentzVector()
            tlv.SetPtEtaPhiM(m.pt, m.eta, m.phi, 0.106)
            z_vector += tlv

        return tlv_particle(z_vector)


    ###################
    ## Output ntuple ##
    ###################

    ''' Here we put all the code to write out interesting
        information to an ntuple '''
    def accept_entry(self):
        if not self._output_tree:
            return

        t = self._output_tree

        # get a reference to the write_branch function (speeds things up)
        write = t.write_branch
        write_obj = t.write_object

        write(self._valid, 'valid')
        if not self._valid:
            # the event's not valid. bail out early
            t.Fill()
            return

        # only write if we don't have a fallback; this prevents
        # rewriting the same stuff multiple times.
        force_write = not self.can_defer()

        if force_write:
            write_obj(self.all_jets, 'jets', ['pt','eta','phi','m'])

        if self._mu_width > 0 or force_write:
            write_obj(self.hard_muons, 'mu', ['pt','eta','phi'])

            if self.z_boson != None:
                write_obj([self.z_boson], 'z', ['pt','eta','phi','m'])

        if self._met_width > 0 or force_write:
            write_obj(self.met_smeared, 'met', ['et', 'phi'])

        t.Fill()



#############################
## Cutflow implementations ##
#############################
''' A very basic (if not very meaningful) analysis cutflow '''


def analysis_cutflow(v):
    v.cut_if(len(v.all_muons) < 2, "2muons")
    v.cut_if(len(v.hard_muons) < 1, "hardmu")
    v.cut_if(v.met_smeared.et < 80, "met80")

''' A control region cutflow, that implements the basic cutflow
    above, and additionally requires a bunch of jets '''


def jetCR_cutflow(v):
    analysis_cutflow(v)

    v.cut_if(len(v.all_jets) < 3, "3jets")


#########################
## Main program driver ##
#########################
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Example variational analysis")
    parser.add_argument('--tree', default='physics',
                        help='the input TTree name')
    parser.add_argument('--out', default='variations.root',
                        help='the output filename')
    parser.add_argument('input_file', nargs='+',
                        help='the input file(s) to use')
    args = parser.parse_args()

    # load up the input files
    input_tree = r.TChain(args.tree)
    map(input_tree.Add, args.input_file)

    # create the output file
    outfile = r.TFile(args.out, 'recreate')

    # set up the variations to be run
    var_nominal = ExampleVariation(process_fn=analysis_cutflow,
                                   name="nominal")

    variations_to_run = [
        ExampleVariation(process_fn=analysis_cutflow,
                         name='smeared muons', mu_width=0.2),
        ExampleVariation(process_fn=analysis_cutflow,
                         name='smeared met', met_width=20),
        ExampleVariation(process_fn=jetCR_cutflow,
                         name='jets CR'),
    ]

    # run the analysis using the variation_loop driver:
    run(input_tree, nominal=var_nominal, variations=variations_to_run, entry_limit=50000)

    outfile.Write()
    outfile.Close()

    # print the results
    print "OKAY Done!"
    print
    for v in variations_to_run:
        print "==== Cutflow: %s ====" % v._name
        print v._cutflow
        print
    print ">>>> Calculation stats: <<<<"
    print_stats()
    print

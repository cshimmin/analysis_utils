import analysis_utils.variation as variation
from pytree import PyTree

'''
 A minor extension of the AnlaysisVariation class, for
 jobs that want to output NTuples.
'''


class AnalysisVariationNTuple(variation.AnalysisVariation):

    def __init__(self, *args, **kwargs):
        variation.AnalysisVariation.__init__(self, *args, **kwargs)

        # create the output ntuple. if not output name is supplied,
        # use the descriptive name, replacing spaces w/ underscores.
        output_name = kwargs.get('output_name', '_'.join(self._name.split()))

        self._output_tree = PyTree(output_name, self._name)

    def get_ntuple(self):
        return self._output_tree

    def reset(self):
        variation.AnalysisVariation.reset(self)

        self._output_tree.reset()

    '''
     The user should override this method, writing out whatever information
     they want to include in the output ntuple. A reference to the underlying
     PyTree is passed as an argument for convenience.
    '''
    def populate_ntuple(self, ntuple):
        print "WARNING! Base class populate_ntuple() invoked for variation `%s`!" % self._name

    ''' This entry was accepted! Set valid flag and fill! '''
    def accept_entry(self):
        t = self._output_tree
        self.populate_ntuple(t)
        t.write_branch(True, '_valid')
        t.Fill()

    '''
     If this instance is rejected, but the entry was accepted for the
     combined analysis, we should write out an empty entry.
    '''
    def reject_entry(self):
        t = self._output_tree
        t.write_branch(False, '_valid')
        t.Fill()

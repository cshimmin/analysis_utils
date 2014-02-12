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
        try:
            output_name = kwargs['output_name']
        except KeyError:
            output_name = '_'.join(self._name.split())
        self._output_tree = PyTree(output_name, self._name)

    def get_ntuple(self):
        return self._output_tree

    def reset(self):
        variation.AnalysisVariation.reset(self)

        self._output_tree.reset()

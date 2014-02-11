#!/usr/bin/env python

import ROOT as r

'''
simple class to load in vector-branches grouped by a common
logical prefix. individual attributes are lazy-loaded.

N.B.: the code assumes there is an associated branch "<prefix>_n" that contains the length
of the vectors for the event. (FIXME?)

for example, suppose you have a TTree with some vector branches which represent muons:
    mu_pt, mu_eta, mu_phi, mu_E

you can write your code as those these muons are objects:
    for evt in tree:
            all_muons = get_objects(tree, 'mu_')

            highpt_muons = [m for m in all_muons if m.pt > 100e3]
            central_muons = [m for m in highpt_muons if m.eta < 1.5]

            # ...
'''
class generic_obj:
    # tree          reference to tree where the object is stored
    # prefix        logical group prefix
    # idx           index in into the vector branches for this object

    def __init__(self, tree, prefix, idx):
        self.tree = tree
        self.prefix = prefix
        self.idx = idx

    def __getattr__(self, attr):
        answer = getattr(self.tree, '%s_%s' % (self.prefix, attr))[self.idx]
        setattr(self, attr, answer)
        return answer

    def serialize(self):
        branches = [b.GetName()[len(self.prefix) + 1:] for b in self.tree.GetListOfBranches()
                    if b.GetName().startswith(self.prefix) and b.GetName() != '%s_n' % self.prefix]
        # print branches
        data = ((b, getattr(self, b)) for b in branches)
        datasane = filter(lambda d: not 'vector' in str(d[1].__class__), data)
        return dict(datasane)


''' conveneince methods to generate/load lists of D3PD objects based on
    their branch prefix '''
def fetch_objects(tree, prefix):
    for i in xrange(getattr(tree, '%s_n' % prefix)):
        obj = generic_obj(tree, prefix, i)
        yield obj

''' Same as above, but load the whole generator into a list '''
def get_objects(tree, prefix):
    return list(fetch_objects(tree, prefix))

''' Build a TLorentzVector from the pt,eta,phi,m attributes
    of the given object, and bind it to the object's
    `tlv` attribute. '''
def build_tlv(obj, mass=None):
    if mass is not None:
        obj.tlv = r.TLorentzVector()
        obj.tlv.SetPtEtaPhiM(obj.pt, obj.eta, obj.phi, mass)
    else:
        obj.tlv = r.TLorentzVector(obj.pt, obj.eta, obj.phi, obj.m)
    return obj

''' Inverse of build_tlv(); build an object from a TLorentzVector. '''
class tlv_particle:
    def __init__(self, tlv):
        self.tlv = tlv
        self.pt = tlv.Pt()
        self.eta = tlv.Eta()
        self.phi = tlv.Phi()
        self.m = tlv.M()

class met_object:
    def __init__(self, et, phi):
        from numpy import cos, sin
        self.et = et
        self.phi = phi
        self.x = et*cos(phi)
        self.y = et*sin(phi)

if __name__ == "__main__":
    pass

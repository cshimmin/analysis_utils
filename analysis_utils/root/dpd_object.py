#!/usr/bin/env python

import ROOT as r

'''
DPDObject is a class that helps read/write objects from
ROOT files in the loosely-defined "DPD" (Derived Physics Data)
format. The common requirements for the format are:
    - objets are grouped by a common prefix
    - attribute names follow the object prefix, separated by undrescore
    - if a field actually represents a list (or vector) of objects,
      there should also be a <prefix>_n field, indiciating the
      size of the list.

Individual attributes are lazy-loaded from the underlying TTree,
so it is relatively inexpensive to pass around lists of these objects
and filter/map/perform calculations etc on the fly.

For example, suppose you have a TTree with some vector branches which
represent muons:
    mu_pt, mu_eta, mu_phi, mu_E

you can write your code as those these muons are objects:
    for evt in tree:
            all_muons = get_objects(tree, 'mu')

            highpt_muons = [m for m in all_muons if m.pt > 100e3]
            central_muons = [m for m in highpt_muons if m.eta < 1.5]

            # ...
'''
class DPDObject:
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
        obj = DPDObject(tree, prefix, i)
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

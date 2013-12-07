import ROOT as r
import numpy as np

'''
simple tree definitions using python dictionaries

to create a new tree with some branches, do:
	t = setup_tree('awesometree', treedef)

see below for example tree definition

N.B.: due to the fact that python's primitive types are all pass-by-value,
for scalar-type branches, you'll have to use zero-indexing to write values:
	t = setup_tree('physics', {'some_scalar': float})
	t.some_scalar[0] = 3.14
	t.Fill()
'''

# example tree definition
treedef = {
	'leading_ph_pt': float,
	'leading_ph_eta': float,
	'leading_ph_phi': float,
	'leading_ph_E': float,
	'leading_ph_idx': int,
	'jet_corr_pt': [float],
	'jet_corr_eta': [float],
	'jet_corr_phi': [float],
	'jet_corr_E': [float],
	'jet_corr_M': [float],
	'met_wet': [[float]],
	'met_wex': [[float]],
	'met_wey': [[float]],
	}


def setup_tree(name, treedef):
	t = r.TTree(name, name)

	bind_scalar(t, 'valid', int)

	branch_names = sorted(treedef.keys())
	for bname in branch_names:
		btype = treedef[bname]
		bind_any(t, bname, btype)
	
	return t

typenames_long = { float: 'double', int: 'int' }
typenames_short = { float: 'D', int: 'I' }

def bind_any(t, bname, btype):
	if not type(btype) == list:
		bind_scalar(t, bname, btype)
	elif len(btype) and type(btype[0]) == list:
		if len(btype[0]):
			bind_vector2(t, bname, btype[0][0])
		else:
			bind_vector2(t, bname, float)
	elif len(btype):
		bind_vector(t, bname, btype[0])
	else:
		bind_vector(t, bname, float)


def bind_scalar(t, bname, btype):
	v = np.array([0], dtype=btype)
	t.Branch(bname, v, '%s/%s' % (bname, typenames_short[btype]))
	setattr(t, bname, v)

def bind_vector(t, bname, btype):
	v = r.vector(typenames_long[btype])()
	t.Branch(bname, 'vector<%s>'%typenames_long[btype], v)
	setattr(t, bname, v)

def bind_vector2(t, bname, btype):
	v = r.vector('vector<%s>'%typenames_long[btype])()
	t.Branch(bname, 'vector<vector<%s> >'%typenames_long[btype], v)
	setattr(t, bname, v)

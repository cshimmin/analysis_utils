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

class PyTree(r.TTree):
	def __init__(self, *args, **kwargs):
		r.TTree.__init__(self, *args)

		self.__branch_cache = {}

	def reset(self):
		for v, btype in self.__branch_cache.values():
			# set the values to an appropriate
			# state depending on thier type
			if type(btype) == list:
				# the pointer will be a vector type.
				# call clear on it.
				v.clear()
			else:
				# the pointer is to a numpy.array with
				# a scalar value. set it to zero.
				v[0] = 0

	def write_branch(self, value, bname, btype):
		try:
			v, _ = self.__branch_cache[bname]
		except KeyError:
			# oops haven't made this branch yet.
			v = bind_and_backfill(self, bname, btype)
			self.__branch_cache[bname] = (v, btype)

		# now we have a pointer to the branch memory.
		# write the value depending on the type
		if type(btype) == list:
			# some vector type
			if btype[0] == list:
				# TODO!
				raise TypeError('Unsupported type: %s' % btype)
			# okay, just a normal vector.
			# copy the input array with push_back
			map(v.push_back, value)
		else:
			# some sclar type
			v[0] = value

typenames_long = { float: 'double', int: 'int' }
typenames_short = { float: 'D', int: 'I' }

def bind_and_backfill(t, bname, btype):
	v = bind_any(t, bname, btype)

	b = t.GetBranch(bname)
	if t.GetEntries() > 0:
		# tree has already started filling! backfill the new branch
		# with blank values
		for i in xrange(t.GetEntries()):
			b.Fill()

	return v

def bind_any(t, bname, btype):
	if not type(btype) == list:
		v = bind_scalar(t, bname, btype)
	elif len(btype) and type(btype[0]) == list:
		if len(btype[0]):
			v = bind_vector2(t, bname, btype[0][0])
		else:
			v = bind_vector2(t, bname, float)
	elif len(btype):
		v = bind_vector(t, bname, btype[0])
	else:
		v = bind_vector(t, bname, float)
	
	return v
	

def bind_scalar(t, bname, btype):
	v = np.array([0], dtype=btype)
	b = t.Branch(bname, v, '%s/%s' % (bname, typenames_short[btype]))
	setattr(t, bname, v)

	return v


def bind_vector(t, bname, btype):
	v = r.vector(typenames_long[btype])()
	b = t.Branch(bname, 'vector<%s>'%typenames_long[btype], v)
	setattr(t, bname, v)

	return v

def bind_vector2(t, bname, btype):
	v = r.vector('vector<%s>'%typenames_long[btype])()
	b = t.Branch(bname, 'vector<vector<%s> >'%typenames_long[btype], v)
	setattr(t, bname, v)

	return v

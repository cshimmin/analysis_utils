#!/usr/bin/env python

'''
simple class to load in vector-branches grouped by a common
logical prefix. individual attributes are lazy-loaded.
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
		answer = getattr(self.tree, '%s_%s'%(self.prefix,attr))[self.idx]
		setattr(self, attr, answer)
		return answer
	def serialize(self):
		branches = [b.GetName()[len(self.prefix)+1:] for b in self.tree.GetListOfBranches() if b.GetName().startswith(self.prefix) and b.GetName() != '%s_n'%self.prefix]
		#print branches
		data = ( (b, getattr(self, b)) for b in branches)
		datasane = filter(lambda d: not 'vector' in str(d[1].__class__), data)
		return dict(datasane)

# conveneince methods to generate/load lists of D3PD objects based on their branch prefix
def fetch_objects(tree, prefix):
	for i in xrange(getattr(tree,'%s_n'%prefix)):
		obj = generic_obj(tree, prefix, i)
		yield obj

# same as above, but load the generator into a list
def get_objects(tree,prefix):
	return [o for o in fetch_objects(tree, prefix)]

if __name__ == "__main__":
	pass

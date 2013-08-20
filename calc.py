#!/usr/bin/env python

import inspect
import ROOT as r

'''
  Exception to be thrown in a calculation fails
'''
class CalcError(Exception):
	def __init__(self, msg, code=0):
		self.msg = msg
		self.code = code
	def __repr__(self):
		return self.msg
	def __str__(self):
		return self.__repr__()

'''
  Base class for 'calculable" trees
'''
class CalcTree(r.TChain):
	def __init__(self, *args):
		r.TChain.__init__(self, *args)

		# set up a list of calculable items by sniffing out methods
		# named _get_xxxx(). Save a reference to the instance method
		# for later.
		self._calculables = dict([ (n[5:], m) for (n,m) in inspect.getmembers(self)
				if n.startswith('_get_') and inspect.ismethod(m) ])
	
	def reset(self):
		# delete any cached calculables
		for c in self._calculables:
			try:
				delattr(self, c)
			except AttributeError:
				pass

	def __getattr__(self, attr):
		try:
			# used tried to access a calculable item, but it's not cached.
			# calculate and save the result, then return it.
			v = self._calculables[attr]()
			setattr(self, attr, v)
			return v
		except KeyError:
			# we're not managing this attribute, so escalate to TChain
			return r.TChain.__getattr__(self, attr)

if __name__ == "__main__":
	pass

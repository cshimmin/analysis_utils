#!/usr/bin/env python

import inspect

from cutflow import Cutflow, SkipEvent

'''
 Exception to be thrown if a calculation fails.
'''
class CalculationError(Exception):
	def __init__(self, msg, code=0):
		self.msg = msg
	def __repr__(self):
		return self.msg

'''
 Raise this exception if you want to force the fallback
 to respond to the calculation.
'''
class CalculationFallback(Exception):
	def __init__(self):
		pass

'''
 Raise this exception if you want to skip the event during
 the process() stage; e.g. if a cut has failed.
'''
#class SkipEvent(Exception):
#	def __init__(self):
#		pass

'''
 Base class for variational analysis selections
'''
class AnalysisVariation:
	def __init__(self, fallback=None, process_fn=None, name='Variation'):
		self.__calculables = {}
		self.__fallback = fallback

		self.process_fn = process_fn
		self.name = name
		self.warn_once = False

		self.set_valid(False)

		self.cutflow = Cutflow()

		# set up a list of calculable items by sniffing out methods
		# named _get_xxxx(). Save a reference to the instance method
		# for later.
		#self.__calculables = dict([ (n[5:], m) for (n,m) in inspect.getmembers(self)
		#	if n.startswith('_get_') and inspect.ismethod(m) ])

		self.__calculables = dict([ (n[5:], m) for (n,m) in inspect.getmembers(self)
				if n.startswith('_get_') and inspect.ismethod(m) ])

	def set_fallback(self, fallback):
		# not sure if we have to do something clever here yet,
		# in case user calls after initialization
		if fallback == self:
			# this will lead to infinite recursion...
			return
		self.__fallback = fallback
	
	def process(self):
		# this is slow... maybe we should optimize.
		# but we'll put it here as a convenience method.
		try:
			self.process_fn(self)
		except TypeError as e:
			if e.message == "'NoneType' object is not callable":
				if not self.warn_once:
					print "Warning! No process() function supplied for variation `%s`!"%self.name
					self.warn_once = True
			else:
				raise e
	

	def cut_if(self, expr, cutname):
		self.cutflow.cut_if(expr, cutname)
	
	def reset(self):
		# delete any cached calcuable results
		for c in self.__calculables:
			try:
				delattr(self, c)
			except AttributeError:
				# fine, nothing to delete. it was never set.
				pass
		
		# and set state to invalid
		self.set_valid(False)
	
	def set_valid(self, valid):
		self.__valid = valid
	
	def write_ntuple(self):
		if not self.warn_once:
			print "WARNING! Base class write_ntuple() invoked for variation `%s`!"%self.name
			self.warn_once = True
	
	def __getattr__(self, attr):
		# here's the magic. if the requested attribute is calculable,
		# go calculate it and then cache the result.
		try:
			# user tried to access a calculable item, but it's not cached.
			# calculate and save the result, then return it.
			v = self.__calculables[attr]()
			setattr(self, attr, v)
			return v
		except KeyError, CalculationFallback:
			# we're not managing this attribute, so escalate to the
			# "fallback" object (which by default is the underlying
			# TTree):
			return getattr(self.__fallback, attr)

	def __str__(self):
		return "<Varation object `%s`>"%self.name

if __name__ == "__main__":
	print "Come back later!"


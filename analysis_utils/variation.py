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
 Base class for variational analysis selections
'''
class AnalysisVariation:

    def __init__(self, source=None, process_fn=None, name='Variation', fallback=None, **kwargs):
        self._calculables = {}
        self._source = source
        self._fallback = fallback

        self._process_fn = process_fn
        self._name = name
        self._warn_once = False

        self.set_valid(False)

        self._cutflow = Cutflow()

        # set up a list of calculable items by sniffing out methods
        # named _get_xxxx(). Save a reference to the instance method
        # for later.
        # self._calculables = dict([ (n[5:], m) for (n,m) in inspect.getmembers(self)
        #	if n.startswith('_get_') and inspect.ismethod(m) ])

        self._calculables = dict([(n[5:], m) for (n, m) in inspect.getmembers(self)
                                   if n.startswith('_get_') and inspect.ismethod(m)])

    def set_source(self, source):
        self._source = source

    def set_fallback(self, fallback):
        if fallback == self:
            return
        self._fallback = fallback

    '''
     A convenience method; simply tries to invoke the user-supplied process function.
    '''
    def process_entry(self):
        # NB this is slow... maybe we should optimize.
        # but we'll put it here as a convenience method.
        try:
            self._process_fn(self)
        except TypeError as e:
            if e.message == "'NoneType' object is not callable":
                if not self._warn_once:
                    print "Warning! No process function supplied for variation `%s`!" % self._name
                    self._warn_once = True
            else:
                raise e

    '''
     This method is called if the input entry has been accepted *and* this instance
     passed (i.e. is in the valid state). It may be used, e.g., to write out ntuple branches.
    '''
    def accept_entry(self):
        if not self._warn_once:
            print "WARNING! Base class accept_entry() invoked for variation `%s`!" % self._name
            self._warn_once = True

    '''
     This method is called if the input entry was accepted for *some* variation,
     but this instance did not pass (i.e. this entry is not valid). It may be used,
     e.g., to fill an empty ntuple entry.
    '''
    def reject_entry(self):
        pass

    '''
     Reset the state of all managed calculables. Also set the current entry status
     to invalid for this object.
    '''
    def reset(self):
        # delete any cached calcuable results
        for c in self._calculables:
            try:
                delattr(self, c)
            except AttributeError:
                # fine, nothing to delete. it was never set.
                pass

        # and set state to invalid
        self.set_valid(False)

    def cut_if(self, expr, cutname):
        self._cutflow.cut_if(expr, cutname)

    def defer(self):
        if self._fallback:
            raise CalculationFallback

    def defer_if(self, expr):
        if self._fallback and expr:
            raise CalculationFallback

    def defer_unless(self, expr):
        if self._fallback and not expr:
            raise CalculationFallback

    def can_defer(self):
        return self._fallback is not None

    def set_valid(self, valid):
        self._valid = valid

    def __getattr__(self, attr):
        # here's the magic. if the requested attribute is calculable,
        # go calculate it and then cache the result.
        try:
            # user tried to access a calculable item, but it's not cached.
            # calculate and save the result, then return it.
            v = self._calculables[attr]()
            setattr(self, attr, v)
            return v
        except KeyError:
            # we're not managing this attribute, so escalate to the
            # "source" object (which by default is the underlying
            # TTree):
            return getattr(self._source, attr)
        except CalculationFallback:
            # defer the calculation to the fallback object
            return getattr(self._fallback, attr)

    def __str__(self):
        return "<Varation object `%s`>" % self._name

if __name__ == "__main__":
    print "Come back later!"

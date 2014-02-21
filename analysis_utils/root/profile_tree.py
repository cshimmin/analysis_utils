'''
 A simple class which acts as a drop-in replacement to TTree/TChain.
 Before invoking TTree.__getattr__, it will check to make
 sure the requested branch both exists and is *active*.

 This will slow your analysis down but is useful when 
 developing new code, to help make sure you're not messing
 up any variable names.

 Usage is very simple: simply replace the TChain constructor.

 So this:
   import ROOT as r
   t = r.TChain('mytree')
   t.Add('somefile.root')

 becomes this:
   import analysis_utils.root.profile_tree as prof
   t = prof.ProfileChain('mytree')
   t.Add('somefile.root')

 You may optionally set the profiling behavior (default is `fail`):
   t.set_behavior(prof.activate | prof.record)
 
 If you have specified prof.record behavior, you can print a
 summary of branch access records with `print_report()`.

 The three supported profiling modes (which may be bitwise
 OR'd together) are:
   fail     -- raise an attribute error when disabled branches
                 are accessed
   record   -- keep track of the number of times each branch
                 is accessed
   activate -- activate disabled branches when accessed

'''

import ROOT as r

fail = 1
record = 2
activate = 4
class ProfileBase(object):
    def __init__(self, behavior=fail):
        self._branch_list = set()
        self._behavior = behavior
        self._access_list = {}

    def _update_branchlist(self):
        blist = self.GetListOfBranches()
        if blist:
            self._branch_list = set([b.GetName() for b in blist])
        print "updated branch list (%d branches)"%(len(self._branch_list))

    def set_behavior(self, behavior):
        self._behavior = behavior

    def print_report(self):
        if len(self._access_list) == 0:
            print "(no records)"
            return

        name_width = max(map(len, self._access_list.keys()))
        for k,v in self._access_list.items():
            padding = name_width-len(k)+2
            print "%s:%s%d\n" % (k, " "*padding, v)

    def __getattr__(self, attr):
        if attr in self._branch_list:
            if not self.GetBranchStatus(attr):
                if self._behavior & fail:
                    raise AttributeError("Error: requested branch '%s' is inactive!"%attr)
                if self._behavior & activate:
                    print "Warning: activating requested branch '%s'!"%attr
                    self.SetBranchStatus(attr, True)
                    # still need to force a reload, or else the branch data will be empty
                    self.GetEntry(self.GetReadEntry())

            if self._behavior & record:
                try:
                    self._access_list[attr] += 1
                except KeyError:
                    self._access_list[attr] = 1

        return super(ProfileBase, self).__getattr__(attr)

class ProfileChain(ProfileBase, r.TChain):
    def __init__(self, *args, **kwargs):
        ProfileBase.__init__(self, kwargs.get('behavior', fail))
        r.TChain.__init__(self, *args)

        self._update_branchlist()

    def Add(self, *args, **kwargs):
        r.TChain.Add(self, *args, **kwargs)
        self._update_branchlist()

    def Branch(self, *args, **kwargs):
        r.TChain.Branch(self, *args, **kwargs)
        self._update_branchlist()


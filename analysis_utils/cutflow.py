'''
 Raise this exception if you want to skip the event during
 the process() stage; e.g. if a cut has failed.
'''


class SkipEvent(Exception):

    def __init__(self):
        pass


class Cutflow:

    def __init__(self):
        self.cut_names = []
        self.cut_counts = {}

    def cut_if(self, expr, cut_name):
        if expr:
            raise SkipEvent
        else:
            try:
                self.cut_counts[cut_name] += 1
            except KeyError:
                self.cut_counts[cut_name] = 1
                self.cut_names.append(cut_name)

    def __repr__(self):
        if len(self.cut_names) == 0:
            return "(no cuts)"

        rep_str = ""
        name_width = max(map(len,self.cut_names))
        for cut in self.cut_names:
            padding = name_width-len(cut)
            rep_str += "%s:%s\t%d\n" % (cut, " "*padding, self.cut_counts[cut])
        return rep_str

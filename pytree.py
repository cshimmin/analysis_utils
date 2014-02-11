import ROOT as r
import numpy as np

class PyTree(r.TTree):

    def __init__(self, *args, **kwargs):
        r.TTree.__init__(self, *args)

        self.__branch_cache = {}

        self.verbose = kwargs.get('verbose', False)

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

    def write_branch(self, value, bname, btype=None):
        try:
            v, _ = self.__branch_cache[bname]
        except KeyError:
            if btype == None:
                try:
                    btype = infer_btype(value)
                except EmptyValue:
                    # the value was iterable, but empty. just move on
                    # for now, since we cannot infer the type. the
                    # next call may have a nonempty value, and we will
                    # create the branch then.
                    return

            # oops, haven't made this branch yet. let's do that now:
            v = bind_and_backfill(self, bname, btype)
            self.__branch_cache[bname] = (v, btype)

            if self.verbose:
                print "pytree: Created branch '%s' (type: %s)" % (bname, get_typeclass(btype))


        # now we have a pointer to the branch memory.
        # write the value depending on the type
        if btype in (int, float, bool):
            # just a scalar type; these are managed by numpy.ndarray's:
            v[0] = value
        elif type(btype) == list:
            # some vector type
            if btype[0] == list:
                # TODO!
                raise TypeError('pytree: unsupported type (nested vectors coming soon...)' % btype)
            # just a normal (1-d) vector.
            # copy the input array with push_back
            map(v.push_back, value)


typenames_long = {float: 'double', int: 'int', bool: 'bool'}
typenames_short = {float: 'D', int: 'I', bool: 'O'}

''' Exception to represent type inference failure due to
    an empty iterable. '''
class EmptyValue(TypeError):
    pass

''' Try to invert the appropriate branch type
    for the given value '''
def infer_btype(val):
    t = type(val)

    if t == list:
        if len(val) == 0:
            raise EmptyValue('pytree: cannot infer type from empty iterable.')
        return [infer_btype(val[0])]
    elif t == tuple:
        return tuple( infer_btype(v) for v in val )
    elif t in (int, float, bool):
        return t
    elif t == np.ndarray:
        dt = {'i': int, 'f': float}[val.dtype.kind]
        def nest(n):
            return dt if n==0 else [nest(n-1)]
        return nest(len(val.shape))
    else:
        raise TypeError('pytree: unsupported type.')

def get_typeclass(btype):
    if btype in (int, float, bool):
        return typenames_long[btype]

    t = type(btype)
    if t == list:
        return 'vector< %s >' % get_typeclass(btype[0])
    elif t == tuple:
        raise TypeError('pytree: unsupported type (tuples are coming soon...)')
    else:
        raise TypeError('pytree: unsupported type.')


def bind_and_backfill(t, bname, btype):
    v = bind_any(t, bname, btype)

    b = t.GetBranch(bname)
    if t.GetEntries() > 0:
        # tree has already started filling! backfill the new branch
        # with blank values
        for i in xrange(t.GetEntries()):
            b.Fill()

    return v


def bind_any(tree, bname, btype):
    if btype in (int, float, bool):
        return bind_scalar(tree, bname, btype)
    
    t = type(btype)
    if t == list:
        if len(btype) == 0:
            raise TypeError('pytree: unsupported type []')

        v = bind_vector(tree, bname, btype)
    else:
        raise TypeError('pytree: unsupported type')

    return v


def bind_scalar(tree, bname, btype):
    v = np.array([0], dtype=btype)
    b = tree.Branch(bname, v, '%s/%s' % (bname, typenames_short[btype]))
    setattr(tree, bname, v)

    return v


def bind_vector(tree, bname, btype):
    v = r.vector( get_typeclass(btype[0]) )()
    b = tree.Branch(bname, get_typeclass(btype), v)
    setattr(tree, bname, v)

    return v

#!/usr/bin/env python

import variation


def run(input_tree, nominal=None, variations=[], **kwargs):
    # set the fallback reference for all the variations.
    for v in variations:
        v.set_source(input_tree)
        v.set_fallback(nominal)

    # make sure that nominal is included in the full list
    if nominal and not nominal in variations:
        nominal.set_source(input_tree)
        variations.append(nominal)

    variations_and_functions = [(v, v._process_fn) for v in variations]

    if len(variations) == 0:
        print "Warning! No variations to process. Aborting..."
        return

    total_entries = input_tree.GetEntries()
    entry_limit = kwargs.get('entry_limit', total_entries+1)
    for i, evt in enumerate(input_tree):
        if i % 5000 == 0:
            print "Processed %d/%d ~ %.2f%%" % (i, total_entries, 100. * i / (total_entries))
            if i>=entry_limit:
                print "Entry limit reached (%d); quitting early." % (entry_limit)
                break

        for v in variations:
            # NB: all variations have to be reset before
            # _any_ run, since they may reference
            # each other's cache (i.e. FallbackCalculation)
            v.reset()

        keep = False
        for v, p in variations_and_functions:
            try:
                p(v)
                v.set_valid(True)
                keep = True
            except variation.SkipEvent:
                # just move on to the next one!
                pass

        if keep:
            # if any of the variations managed to pass, write out everything.
            for v in variations:
                v.accept_entry()

if __name__ == "__main__":
    pass
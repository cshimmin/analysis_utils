#!/usr/bin/env python

import argparse
import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True

TREE_NAME = 'physics'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List branches of a tree in a rootfile")
    parser.add_argument('root_file', type=str,
                        help='Input root file')
    parser.add_argument('--tree', type=str, default="physics",
                        help='The name of the TTree within the root file')
    args = parser.parse_args()

    f = r.TFile(args.root_file)
    t = f.Get(args.tree)

    for b in t.GetListOfBranches():
        print b.GetName()

#!/usr/bin/env python

import os
import argparse
import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True

from branch import match_branches_from_file

TREE_NAME = 'physics'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Keep only branches that match expressions in a file.")
    parser.add_argument('branch_spec', type=str,
                        help="The file containing expressions to match. Lines beginning with # are comments")
    parser.add_argument('root_file', type=str, nargs="+",
                        help='Either a whitespace- or comma-delimited list of root files to filter')
    parser.add_argument('--remove', action='store_true')
    parser.add_argument('--out', type=str, default="",
                        help='Output directory for filtered files. By default, output to the same directory as the original file.')
    parser.add_argument('--ext', type=str, default="trim",
                        help='Extension added to the end of the output file names')

    args = parser.parse_args()

    input_files = args.root_file
    if len(input_files) == 1 and ',' in input_files[0]:
        input_files = input_files[0].split(',')

    outfiles = []
    for in_file in input_files:
        t0 = r.TChain(TREE_NAME)
        t0.Add(in_file)

        matches = match_branches_from_file(args.branch_spec, t0)

        t0.SetBranchStatus("*", args.remove)

        print "Matched branches:"
        for b in matches:
            print " ", b
            t0.SetBranchStatus(b, not args.remove)

        if args.out == "":
            out_file_name = "%s.%s" % (in_file, args.ext)
        else:
            out_file_name = os.path.join(
                args.out, os.path.basename("%s.%s" % (in_file, args.ext)))

        outfiles.append(out_file_name)

        out_file = r.TFile(out_file_name, "RECREATE")
        t1 = t0.CloneTree()
        t1.Write()
        out_file.Close()

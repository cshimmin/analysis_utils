import ROOT as r
import re


def match_branches_from_file(selection_files, tree):
    # load regular expression from file
    if not type(selection_files) == list:
        selection_files = [selection_files]

    selections = []
    for f in selection_files:
        selections.extend(open(f).readlines())
    return match_branches(selections, tree)


def match_branches(selections, tree):
    if not type(selections) == list:
        selections = [selections]

    regexs = []
    for line in selections:
        # ditch whitespace (regex should use $^ delims if necessary)
        line = line.strip()
        if line == '' or line.startswith('#'):
            continue  # ditch blank lines and comments
        regexs.append(re.compile(line))

    all_branches = [b.GetName() for b in tree.GetListOfBranches()]

    # keep only branches that match at least one of the selection strings
    matched_branches = filter(
        lambda b: any((regex.match(b) is not None for regex in regexs)), all_branches)
    return matched_branches

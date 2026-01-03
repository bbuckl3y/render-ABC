# -*- coding: utf-8 -*-
"""
Code to extract a tune/song-list extract CSV file from an ABC library

It expects abcsvg.py set separators.
"""

import os
import re
import sys
import csv

pt=''

def main():
    assert len(sys.argv)==3, "usage: "+sys.args[0]+" abcfile outfile.csv"
    assert sys.argv[2].endswith(".csv"), "Output file must be CSV file (filename ends with .csv)"

    # build a list of sets
    # each set is a list of tuples with the Xid and the title of the first title in the tune

    xid, sets, sx = None, [], []
    with open(sys.argv[1]) as src:
        for r in src:
            rs = r.strip()
            if any(rs.startswith(sep) for sep in ['%%newpage', "%%sep"]):
                sets.append(sx)
                sx =[] # new set - starts as empty

            # strip trailing ABC notation comments
            cpos = rs.find('%')
            if cpos>=0:
                rs = rs[:cpos]
            
            # only X: and T: lines matter in this
            if rs.startswith('X:'):
                tmp = rs[2:].strip().split()
                xid = tmp[0] if tmp else None
            if xid and rs.startswith("T:"): # first T: after non-empty X: 
                sx.append((xid, rs[2:].strip()))
                xid = None

    # process last tune/set
    if sx:
        if sets:
            sets.append(sx)
        else:
            # read an ABC library with no separators
            sets = [[x] for x in sx]
    
    if not sets: # error if no tunes/sets found - no output
        print("no tunes/sets found.")
        exit(1)
    
    # output the CSV file
    with open(sys.argv[2],"wt") as dstf:
        dst = csv.writer(dstf, dialect="excel")
        dst.writerow(("set", "title", "from"+sys.argv[1].rsplit('/',1)[-1]))
        # xids separated by '-' plus first title
        dst.writerows(('-'.join(x[0] for x in xs), xs[0][1]) for xs in sets) # force Xids as numbers - start with '

    return

if __name__=="__main__":
    main()
        
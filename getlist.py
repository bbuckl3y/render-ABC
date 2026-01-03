# -*- coding: utf-8 -*-

import os
import re
import sys

pt=''

def main():
    assert len(sys.argv)==3
    x = sys.argv[1]
    if not x.startswith('/'):
        x = os.path.join(os.getcwd(), x)
    x = x.replace('/./', '/')
    x = re.sub(r'/\.\./[^/]*/', '/', x)
    with open(x) as src, open(sys.argv[2], "wt") as dst:
        def fx(xx, tx, nx):
            global pt
            if xx and tx:
                if nx:
                    t, ds = nx.split(':',1)
                    if t and t!=pt:
                        print('#T:'+t, file=dst)
                        pt = t
                    print('#D:'+ds, file=dst)
                print('1', xx, '-', tx, sep='\t', file=dst)
            return None, None, None
        print('@'+x, file=dst)
        xx, tx, nx = None, None, None
        for r in src:
            rs = r.strip()
            if rs.startswith('%%newpage'):
                xx, tx, nx = fx(xx, tx, nx)
                print(file=dst)
            elif r.startswith('X:'):
                xx, tx, nx = fx(xx, tx, nx)
                xx = rs[2:].strip()
            elif r.startswith('T:'):
                if not tx:
                    tx = rs[2:].strip()
            elif re.match(r'N:.*:.+', r):
                nx = r[2:].strip()
        xx, tx, nx = fx(xx, tx, nx)

    return

if __name__=="__main__":
    main()
        
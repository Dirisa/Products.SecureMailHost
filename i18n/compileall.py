#!/usr/bin/env python

import os, glob

for f in glob.glob('*po') + glob.glob('*.pot'):
    
    base,suffix = os.path.splitext(f)
    cmd = 'msgfmt -o %s.mo %s' % (base, f)
    print cmd
    os.system(cmd)


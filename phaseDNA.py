#!/usr/bin/env python

import sys
import dna      
                    
infiles_child = (sys.argv[1],)
infiles_father = (sys.argv[2],)
infiles_mother = (sys.argv[3],)

c = dna.Genome(infiles_child,'child')
print c

f = dna.Genome(infiles_father,'father')
print f

m = dna.Genome(infiles_mother,'mother')
print m


c.phase(f,m)

#!/usr/bin/env python

import sys
import dna

g1 = dna.Genome(sys.argv[1].split(','),sys.argv[1])
print g1

g2 = dna.Genome(sys.argv[2].split(','),sys.argv[2])      
print g2

g1.compare(g2,file('diffs.txt','w'))


#!/usr/bin/env python

import sys
import dna      

a = dna.Genome((sys.argv[1],),'A')
b = dna.Genome((sys.argv[2],),'B')

print a
print b

ckeys = a.chromosomes.keys()
ckeys.sort()
for clabel in ckeys:
  if clabel != 'MT' and clabel != 'Y' and clabel != 'X':
    print clabel
    c = a.chromosomes[clabel]
    positions = c.keys()
    positions.sort()
    matchStart = None
    matchLength = 0
    for p in positions:
      sa = c[p]
      sb = b.chromosomes[clabel][p]
      if sa.hasGenotype() and sb.hasGenotype():
        if sa.matches(sb):
          if matchStart is None:
            matchStart = p
          matchLength += 1
        else:
          if matchLength > 700:
            print 'start:',matchStart,'end:',p,'count:',matchLength
          matchStart = None
          matchLength = 0



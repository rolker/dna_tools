#!/usr/bin/env python

import dna      
                    
infiles_23andme = ('genome_Roland_Arsenault_Full_20131015103142_23andme.zip',)
infiles_ftdna = ('N109286-autosomal-o37-results.csv.gz','N109286-x-chromosome-o37-results.csv.gz')


g23 = dna.Genome(infiles_23andme,'23andMe')
print g23

gftdna = dna.Genome(infiles_ftdna,'FamilyTreeDNA')
print gftdna

g23.compare(gftdna,file('diffs.txt','w'))

#for c in g23.chromosomes.keys():
    #if c in gftdna.chromosomes:
        #print c
        #matches = 0
        #misses = 0
        #diffs = 0
        #for snp in g23.chromosomes[c].keys():
            #if snp in gftdna.chromosomes[c]:
                #matches += 1
                #if g23.chromosomes[c][snp].result != gftdna.chromosomes[c][snp].result:
                    #diffs += 1
                    ##print g23.chromosomes[c][snp],'!=',gftdna.chromosomes[c][snp]
            #else:
                #misses += 1
        #print 'misses:',misses,'matches:',matches,'diffs:',diffs
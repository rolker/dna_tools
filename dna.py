#!/usr/bin/env python

import zipfile
import gzip

class SNP:
    def __init__(self,data):
        self.rsid = data[0].strip('"')
        self.chromosome = data[1].strip('"')
        if len(self.chromosome) == 1 and self.chromosome.isdigit():
            self.chromosome = '0'+self.chromosome
        self.position = int(data[2].strip('"'))
        self.genotype = data[3].strip('"')
        if self.genotype == '--':
          self.genotype = None
        elif self.chromosome == 'X' and len(self.genotype) == 2:
          self.genotype = self.genotype[0]

    def __str__(self):
        return " ".join((self.rsid,self.chromosome,str(self.position),str(self.genotype)))

    def hasAllel(self,a):
      if self.genotype is not None:
        return a in self.genotype
      return False
    
    def otherAllel(self,a):
      if not self.hasAllel(a):
        return None
      if self.genotype[0] == a:
        return self.genotype[1]
      return self.genotype[0]
    
    def hasGenotype(self):
      return self.genotype is not None

    def isHomozygous(self):
      return  self.genotype is not None and self.genotype[0] == self.genotype[1]

    def isHeterozygous(self):
      return  self.genotype is not None and self.genotype[0] != self.genotype[1]
    
    def matches(self,other):
      if self.genotype[0] == other.genotype[0]:
        return True
      if len(self.genotype) == 2 and len(other.genotype) == 2:
        return self.genotype[0] == other.genotype[1] or self.genotype[1] == other.genotype[0] or self.genotype[1] == other.genotype[1]
      return False

class Genome:
    def __init__(self,files,label=None):
        self.label = label
        self.chromosomes = {}

        for f in files:
            print f
            if f.endswith('.zip'):
                inz = zipfile.ZipFile(f,'r')
                for zinfo in inz.infolist():
                    self.read(inz.open(zinfo))
            if f.endswith('.gz'):
                self.read(gzip.GzipFile(f,'r'))
                    

    def read(self,infile):
        sep = None
        for l in infile:
            if len(l) and l[0] != '#':
                if l.startswith('RSID'):
                    if ',' in l:
                        sep = ','
                else:
                    parts = l.strip().split(sep)
                    snp = SNP(parts)
                    if not snp.chromosome in self.chromosomes:
                        self.chromosomes[snp.chromosome] = {}
                    self.chromosomes[snp.chromosome][snp.position] = snp

    def __str__(self):
        clist = self.chromosomes.keys()
        clist.sort()
        ret = []
        if self.label is not None:
            ret.append(self.label)
        for c in clist:
            ret.append(c+' '+str(len(self.chromosomes[c])))
        return '\n'.join(ret)

    def compare(self,other,diffFile = None):
        all_cromes = self.chromosomes.keys()
        for c in other.chromosomes.keys():
            if not c in all_cromes:
                all_cromes.append(c)
        all_cromes.sort()
        total_tcount = 0
        total_ocount = 0
        total_matches = 0
        total_nulls = 0
        total_transposes = 0
        total_diffs = 0
        
        for c in all_cromes:
            tcount = 0
            if c in self.chromosomes:
                tcount = len(self.chromosomes[c])
            ocount = 0
            if c in other.chromosomes:
                ocount = len(other.chromosomes[c])

            total_tcount += tcount
            total_ocount += ocount
            
            print 'Chromosome',c+':',self.label,tcount,'SNPs,',other.label,ocount,'SNPs'
            if c in self.chromosomes and c in other.chromosomes:
                matches = 0
                diffs = 0
                transposes = 0
                nulls = 0
                for position,snp in self.chromosomes[c].iteritems():
                    if position in other.chromosomes[c]:
                        matches += 1
                        if snp.genotype is None or other.chromosomes[c][position].genotype is None:
                            nulls += 1
                        elif snp.genotype != other.chromosomes[c][position].genotype:
                            if len(snp.genotype) == 2 and snp.genotype[0] == other.chromosomes[c][position].genotype[1] and snp.genotype[1] == other.chromosomes[c][position].genotype[0]:
                                transposes += 1
                            else:
                                diffs += 1
                                if diffFile is not None:
                                    diffFile.write(c+','+str(position)+','+snp.genotype+','+other.chromosomes[c][position].genotype+'\n')
                total_matches += matches
                total_nulls += nulls
                total_transposes += transposes
                total_diffs += diffs
                print '\tcommon SNPs:',matches,'nulls (one or both):',nulls,'transposes:',transposes,'different results:',diffs,'({:.2%} disagreement)'.format(diffs/float(matches))
            else:
                print '\tno matching SNPs'
        print 'All:',self.label,total_tcount,'SNPs,',other.label,total_ocount,'SNPs'
        print '\tcommon SNPs:',total_matches,'nulls (one or both):',total_nulls,'transposes:',total_transposes,'different results:',total_diffs,'({:.2%} disagreement)'.format(total_diffs/float(total_matches))

    def phase(self,p1,p2):
      ckeys = self.chromosomes.keys()
      ckeys.sort()
      mutations = 0
      for clabel in ckeys:
        if clabel != 'MT' and clabel != 'Y' and clabel != 'X':
          print clabel
          c = self.chromosomes[clabel]
          positions = c.keys()
          positions.sort()
          for p in positions:
            sc = c[p]
            sp1 = p1.chromosomes[clabel][p]
            sp2 = p2.chromosomes[clabel][p]
            
            gc = sc.genotype
            
            gp1 = sp1.genotype
            gp2 = sp2.genotype
            p1c = '?'
            p2c = '?'
            p1nc = '?'
            p2nc = '?'
            mutation = False

            if not sc.hasGenotype():
              if sp1.isHomozygous():
                p1c = sp1.genotype[0]
                p1nc = p1c
              if sp2.isHomozygous():
                p2c = sp2.genotype[0]
                p2nc = p2c
              sc.phase = p1c+p2c

            if sc.isHomozygous():
              sc.phased = sc.genotype
              if sp1.hasAllel(gc[0]):
                p1c = gc[0]
                p1nc = sp1.otherAllel(p1c)
              elif not sp1.hasGenotype():
                p1c = gc[0]
              else:
                mutation = True
              if sp2.hasAllel(gc[1]):
                p2c = gc[1]
                p2nc = sp2.otherAllel(p2c)
              elif not sp2.hasGenotype():
                p2c = gc[1]
              else:
                mutation = True

            if sc.isHeterozygous():
              if sp1.hasAllel(gc[0]) and sp2.hasAllel(gc[1]):
                if not (sp2.hasAllel(gc[0]) and sp1.hasAllel(gc[1])):
                  p1c = gc[0]
                  p1nc = sp1.otherAllel(p1c)
                  p2c = gc[1]
                  p2nc = sp2.otherAllel(p2c)
              elif sp1.hasAllel(gc[1]) and sp2.hasAllel(gc[0]):
                if not (sp2.hasAllel(gc[1]) and sp1.hasAllel(gc[0])):
                  p1c = gc[1]
                  p1nc = sp1.otherAllel(p1c)
                  p2c = gc[0]
                  p2nc = sp2.otherAllel(p2c)
              if not sp1.hasGenotype() and sp2.isHomozygous():
                if sc.hasAllel(gp2[0]):
                  p2c = gp2[0]
                  p2nc = p2c
                  p1c = sc.otherAllel(p2c)
              if not sp2.hasGenotype() and sp1.isHomozygous():
                if sc.hasAllel(gp1[0]):
                  p1c = gp1[0]
                  p1nc = p1c
                  p2c = sc.otherAllel(p1c)
                  
                
            phase =  '  '+p1c+ ' '+p2c
            phase += '  '+p1c+ ' '+p1nc
            phase += '  '+p2c+ ' '+p2nc

            if mutation:
              phase += ' mutation'
              mutations += 1
              
            if not (sc.isHeterozygous() and sp1.isHeterozygous() and sp2.isHeterozygous) and '?' in phase:
              if sc.hasGenotype() or sp1.hasGenotype() or sp2.hasGenotype():
                if gp1 is None:
                  gp1 = '--'
                if gp2 is None:
                  gp2 = '--'
                if gc is None:
                  gc = '--'
                print clabel,str(p), gc ,gp1,gp2,phase, sc.rsid

      print mutations,'mutations'
            

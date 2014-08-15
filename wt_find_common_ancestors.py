#!/usr/bin/env python

import sys
import json
import wt
import codecs
import urllib
import datetime
import StringIO
import time

class WTCache:
  def __init__(self, connection, fname=None):
    self.connection = connection
    self.cache = {}
    self.file = None
    if fname is not None:
      try:
        self.file = open(fname,'r+')
        for l in self.file.readlines():
          data = json.load(StringIO.StringIO(l))
          self.cache[int(data[0]['user_id'])] = data
      except (IOError):
        self.file = open(fname,'w')
      
  def get(self,uid):
    if uid in self.cache:
      return self.cache[uid][0]['person']
    ret = None
    while ret is None:
      p = self.connection.getPage('action=getPerson&key='+str(uid)+'&fields=Name,FirstName,LastNameCurrent,Parents')
      if p is not None:
        datastr = p.read()
        try:
          data = json.load(StringIO.StringIO(datastr))
          self.cache[int(data[0]['user_id'])] = data
          if self.file is not None:
            self.file.write(datastr+'\n')
          ret = data[0]['person']
        except (ValueError):
          print 'error fetching',uid
          time.sleep(.5)
    return ret


start_profiles = []
steps = 10
out = None
cachefn = None

for a in sys.argv[1:]:
    if '=' in a:
        parts = a.split('=',1)
        if parts[0] == 'steps':
            steps = int(parts[1])
        if parts[0] == 'out':
            out = parts[1]
        if parts[0] == 'cache':
          cachefn = parts[1]
            
    else:
      start_profiles.append(a)

c = wt.Connection()
if len(start_profiles) == 0:
  start_profiles.append(c.uname)

cache = WTCache(c,cachefn)

profiles = {}

outfile = None
if out is not None:
  outfile = codecs.open(out,'w',encoding='utf-8')
  outfile.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head><body>\n')


for p in start_profiles:    
  print 'profile:',p,'steps',steps

  data = json.load(c.getPage('action=getPerson&key='+p+'&fields=Id'))
  
  
  toCheck = []
  checked = []
  links = {}
  profiles[p] = {}
  
  toCheck.append(data[0]['person']['Id'])
  links[data[0]['person']['Id']] = None
  
  if out is not None:
    outfile.write('<h1>'+p+'</h1>\n')
  
  total_count = 1
  
  for step in range(steps+1):
      newToCheck = []
      if outfile is not None:
          outfile.write('<h1>Step '+str(step)+'</h1>\n')
      count = 1
      for uid in toCheck:
          checked.append(uid)
          data = cache.get(uid)
          if data is not None:
            profiles[p][uid] = data
            print total_count, step,'steps, ',count,'of',len(toCheck),data['Name'],
            name = ''
            if 'FirstName' in data:
                name += data['FirstName']+' '
                print data['FirstName'],
            if 'LastNameCurrent' in data:
                name += data['LastNameCurrent']+' '
                print data['LastNameCurrent'],
            if links[uid] is not None:
              print '(link:',links[uid][1],profiles[p][links[uid][0]]['Name'],')'
            count += 1
            total_count += 1
            if outfile is not None:
                outfile.write('Steps: '+str(step)+' <a id="'+p+'_'+data['Name']+'" href="http://www.wikitree.com/wiki/'+data['Name']+'">'+data['Name']+'</a>: '+name)
                if links[uid] is not None:
                  outfile.write(' (via: '+links[uid][1]+' <a href="#'+p+'_'+profiles[p][links[uid][0]]['Name']+'">'+profiles[p][links[uid][0]]['Name']+'</a>)')
                outfile.write('<br>\n')
                outfile.flush()
            if type(data['Parents']) == type({}):
                for id in data['Parents'].keys():
                    id = int(id)
                    if not (id in toCheck or id in checked or id in newToCheck):
                        newToCheck.append(id)
                    if not id in links:
                      links[id] = (uid,'child')
            #print checked
            #print toCheck
            #print newToCheck
          else:
            print 'error fetching',uid
      toCheck = newToCheck
      
  print len(checked),'checked'
  
common_profiles = {}

for p in start_profiles:    
  for pk in profiles[p].keys():
    if not pk in common_profiles:
      common_profiles[pk]=[p,]
    else:
      common_profiles[pk].append(p)

if outfile is not None:
  outfile.write('<br><br>\n')


for i in range(len(start_profiles),1,-1):
  if outfile is not None:
    outfile.write('<h2>'+str(i)+' matches</h2>\n')

  for k,v in common_profiles.iteritems():
    if len(v) == i:
      data = profiles[v[0]][k]
      name = ''
      if 'FirstName' in data:
          name += data['FirstName']+' '
          print data['FirstName'],
      if 'LastNameCurrent' in data:
          name += data['LastNameCurrent']+' '
          print data['LastNameCurrent'],
      print v
      if outfile is not None:
        outfile.write('<a id="'+data['Name']+'" href="http://www.wikitree.com/wiki/'+data['Name']+'">'+data['Name']+'</a>: '+name)
        for d in v:
          outfile.write(' ('+d+')')
        outfile.write('<br>\n')
        outfile.flush()


if outfile is not None:
    outfile.write('</body></html>')
      
      
      
#!/usr/local/bin/python
# Minimun numbers of rows in categoryes
HITS_ROWS = 5
# Numbers of rows in user_ip (user_name)
NAMES_ROWS = 30

USAGE = """
$ rejik-stat.py -f log_file [-d]
rejik-stat (Get info in human-readable format from rejik log file)
by Oleg Palij <xmpp://malik@jabber.te.ua>"""

# Main data store - dictionary  { 'user_ip':, 'user_name':, 'category':, 'hits': }. 'hits' - number of hits to 'category' by 'user_name' from 'user_ip'
db = []
# data store for categoryes - dictionary  { 'category': , 'len': }. 'len' - number of rows ranked by 'category' 
categoryes = []
# data store for users - dictionary { 'user_ip': , 'user_name': }
users = []

def parse_line(line):
    """ Parse one line, return dictionary of 'category', 'user_ip', 'user_name' """
    try:
       line = line.replace('\n','')
       line = line.split()
       category = line[2].replace(':','')
       user_ip = line[3]
       user_name = line[4]
       if options.STRIP_DOMAINS:
          match = re.search(r'\\',user_name)
          if match:
             user_name = user_name[match.end():]
    except:
       print 'Sorry, it is possible, that log file contain errors.'
    else:
       return { 'category': category, 'user_ip': user_ip, 'user_name': user_name }

def get_user_category_hits(db, user_ip, user_name, category):
    """ Return 'user_name' from 'user_ip' 'hits' in 'category' from 'db', otherwise return 0 """
    for i in xrange(0, len(db)):
        if (user_ip == db[i]['user_ip']) and (user_name == db[i]['user_name']) and(category == db[i]['category']):
           return db[i]['hits']
    return 0

from optparse import OptionParser
from sys import stderr, exit

parser = OptionParser(usage=USAGE)
parser.add_option("-f", dest="log_file", default='redirector.log',
                     help="rejik log file name")
parser.add_option("-d", "--debug",
                     action="store_true", dest="DEBUG", default=False,
                     help="go into debug mode")
parser.add_option("--strip-domains",
                     action="store_true", dest="STRIP_DOMAINS", default=False,
                     help="strip domain part in user name")

(options, args) = parser.parse_args()

try:
   fh = open(options.log_file)
except:
   print >> stderr, 'Problems while opening rejik log file %s'%(options.log_file)
   exit(1)

if options.STRIP_DOMAINS:
   import re

while True:
      line = fh.readline()
      if line == '':
         break
      else:
         stats = parse_line(line)

      HIT = False
      for i in xrange(0, len(categoryes)):
         if stats['category'] == categoryes[i]['category']:
            HIT = True
            break

      if not HIT:
         if len(stats['category']) < HITS_ROWS:
            lenght = HITS_ROWS 
         else:
            lenght = len(stats['category']) 
         categoryes.append( { 'category': stats['category'], 'len': lenght } )

      HIT = False
      for i in xrange(0, len(users)):
          if stats['user_ip'] == users[i]['user_ip'] and stats['user_name'] == users[i]['user_name']:
             HIT = True
             break

      if not HIT:
         users.append( { 'user_ip': stats['user_ip'], 'user_name': stats['user_name'] } )

      HIT = False

      for i in xrange(0, len(db)):
          if (stats['user_ip'] == db[i]['user_ip']) and (stats['user_name'] == db[i]['user_name']) and (stats['category'] == db[i]['category']):
             HIT = True
             break
      if HIT:
         db[i]['hits'] += 1
      else:
         db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )

fh.close()

field = 'IP (UserName)'
print field.ljust(NAMES_ROWS),

for i in xrange(len(categoryes)):
    print categoryes[i]['category'].center(int(categoryes[i]['len'])),
print

for i in xrange(0, len(users)):
    if users[i]['user_name'] == '-':
       field = '%s'%(users[i]['user_ip'])
    else:
       field = str('%s (%s)'%(users[i]['user_ip'], users[i]['user_name']))
    print field.ljust(NAMES_ROWS),

    for j in xrange(len(categoryes)):
        hits = str(get_user_category_hits(db, users[i]['user_ip'], users[i]['user_name'], categoryes[j]['category']))
        print hits.center(categoryes[j]['len']),
    print 

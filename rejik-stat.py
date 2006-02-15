#!/usr/local/bin/python
# -*- coding: koi8-u -*-
# Minimun numbers of rows in categories
HITS_ROWS = 5
# Numbers of rows in user_ip (user_name)
NAMES_ROWS = 28 
# 
HITS_HIGHLIGHT = 500

USAGE = """$ rejik-stat.py [-h] -f log_file [-d] [--strip-domain] [-c <categories>] [-u <users>]
rejik-stat (Get info in human-readable format from rejik log) by Oleg Palij <xmpp://malik@jabber.te.ua>
Example: ./rejik-stat.py --strip-domain -c PORNO,CHAT,IP -u o.palij,10.6.44.38 -f redirector.log -s IP,vv.palij,10.6.100.2
"""

# Main data store - dictionary  { 'user_ip':, 'user_name':, 'category':, 'hits': }. 'hits' - number of hits to 'category' by 'user_name' from 'user_ip'
db = []
# data store for categories - dictionary  { 'category': , 'len': }. 'len' - number of rows ranked by 'category' 
categories = []
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
parser.add_option("-f", dest="log_file",
                     help="rejik log file name")
parser.add_option("-d", "--debug",
                     action="store_true", dest="DEBUG", default=False,
                     help="go into debug mode")
parser.add_option("-u", dest="USERS", type="string",
                     help="To show only that users that comma-separated list includes")
parser.add_option("-c", dest="CATEGORIES", type="string",
                     help="To show only that categories that comma-separated list includes")
parser.add_option("-s", dest="SKIP", type="string",
                     help="To does not show users or categories that comma-separated list includes")
parser.add_option("--strip-domains",
                     action="store_true", dest="STRIP_DOMAINS", default=False,
                     help="strip domain part in user name")
parser.add_option("--html",
                     action="store_true", dest="HTML_OUTPUT", default=False,
                     help="Show result as HTML instead of plain text")

(options, args) = parser.parse_args()

if options.log_file == None:
   print USAGE
   exit(1)

try:
   fh = open(options.log_file)
except:
   print >> stderr, 'Problems while opening rejik log file %s'%(options.log_file)
   exit(1)

try:
   options.CATEGORIES = options.CATEGORIES.split(',')
except:
   options.CATEGORIES = [] 

try:
   options.USERS = options.USERS.lower().split(',')
except:
   options.USERS = []

try:
   options.SKIP = options.SKIP.lower().split(',')
except:
   options.SKIP = []


if options.STRIP_DOMAINS:
   import re

while True:
      line = fh.readline()
      if line == '':
         break
      else:
         stats = parse_line(line)

      """ Gather all unique categories into list of dictionaries 
          categories[ { 'category':, 'len': }, ... ]
      """
      if (((stats['category'] in options.CATEGORIES) or (options.CATEGORIES == [])) and (stats['category'] not in options.SKIP)):
         HIT = False
         for i in xrange(0, len(categories)):
            if stats['category'] == categories[i]['category']:
               HIT = True
               break
         if not HIT:
            if len(stats['category']) < HITS_ROWS:
               lenght = HITS_ROWS 
            else:
               lenght = len(stats['category']) 
            categories.append( { 'category': stats['category'], 'len': lenght } )

      """ Gather all unique 'user_ip' 'user_name' pairs into list of dictionaries 
          users[ { 'user_ip':, 'user_name': }, ... ]
      """
      if (((stats['user_ip'] in options.USERS) or (stats['user_name'] in options.USERS) or (options.USERS == [])) and (stats['user_ip'] not in options.SKIP) and (stats['user_name'].lower() not in options.SKIP)):
         HIT = False
         for i in xrange(0, len(users)):
             if stats['user_ip'] == users[i]['user_ip'] and stats['user_name'] == users[i]['user_name']:
                HIT = True
                break
         if not HIT:
            users.append( { 'user_ip': stats['user_ip'], 'user_name': stats['user_name'] } )

      """ Gather hits for all unique pairs 'user_ip' 'user_name' in 'category' into list of dictionaries
          db[ { 'user_ip':, 'user_name', 'category', 'hits' }, ... ]
      """
      if (((stats['user_ip'] in options.USERS) or (stats['user_name'].lower() in options.USERS) or (options.USERS == [])) and ((stats['category'] in options.CATEGORIES) or (options.CATEGORIES == [])) and ((stats['user_ip'] not in options.SKIP) and (stats['user_name'].lower() not in options.SKIP) and (stats['category'] not in options.SKIP))):
         HIT = False
         for i in xrange(0, len(db)):
             if (stats['user_ip'] == db[i]['user_ip']) and (stats['user_name'] == db[i]['user_name']) and (stats['category'] == db[i]['category']):
                HIT = True
                break
         # if 'user_ip'&'user_name' in 'category' is already in db - increment hits, else - add new entry
         if HIT:
            db[i]['hits'] += 1
         else:
            db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )

fh.close()

# Print title (ips)
field = 'IP (UserName)'
if not options.HTML_OUTPUT:
   print field.ljust(NAMES_ROWS),
else:
   print """
<HTML>
 <HEAD>
  <TITLE>
   Rejik Stats.
  </TITLE>
 </HEAD>
 <BODY BGCOLOR="#DCDCDC">
  <TABLE BORDER=0 ALIGN=CENTER WIDTH=40%%>
   <TR>
    <TD ALIGN=CENTER VALIGN=BOTTOM>
     TOP
    </TD>
   </TR>
   <TR>
    <TD>
     <TABLE BORDER=1 ALIGN=CENTER WIDTH=100%%>
      <tr>
       <td>
        <div STYLE="color: #000080">%s</div>
       </td>
            """%(field)

# Print title (categories)
for i in xrange(len(categories)):
    if not options.HTML_OUTPUT:
       print categories[i]['category'].center(int(categories[i]['len'])),
    else:
       print """<td ALIGN=CENTER>
                 <div STYLE="color: #000080">%s</div>
                </td>"""%(categories[i]['category'].center(int(categories[i]['len'])))
if not options.HTML_OUTPUT:
   print
else:
   print """</tr>
            <tr>"""

for i in xrange(0, len(users)):
    # Print report by users
    if users[i]['user_name'] == '-':
       field = '%s'%(users[i]['user_ip'])
    else:
       field = str('%s (%s)'%(users[i]['user_ip'], users[i]['user_name']))
    if not options.HTML_OUTPUT:
       print field.ljust(NAMES_ROWS),
    else:
       print """<td>
                 %s
                </td>"""%(field)

    # Print hists to 'category' for 'user_ip'&'user_name'
    for j in xrange(len(categories)):
        hits = get_user_category_hits(db, users[i]['user_ip'], users[i]['user_name'], categories[j]['category'])
        if not options.HTML_OUTPUT:
           print str(hits).center(categories[j]['len']),
        else:
           if hits > HITS_HIGHLIGHT:
              hits = """<div STYLE="color: red">%s</div>"""%(hits)
           print """<td ALIGN=CENTER>
                     %s
                    </td>"""%(hits)
    if not options.HTML_OUTPUT:
       print
    else:
       print """</tr>"""

if not options.HTML_OUTPUT:
   print
else:
   print """</TABLE>
 </TD>
</TR>
</TABLE>
 </BODY>
</HTML>"""

exit(0)

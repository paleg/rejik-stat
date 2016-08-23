#!/usr/bin/env python

import re
from optparse import OptionParser
from sys import stderr, exit

# Minimun numbers of rows in categories (plain text view)
HITS_ROWS = 5
# Minimum numbers of rows in user_ip (user_name) (plain text view)
NAMES_ROWS = 35
# Highlight hits which > then HITS_HIGHLIGHT (html view)
HITS_HIGHLIGHT = 300

USAGE = """$ rejik-stat.py [-h] -f log_file [-d] [--strip-domain] [-c <categories>] [-u <users>]
rejik-stat (Get info in human-readable format from rejik log) by Oleg Palij (mailto,xmpp:o.palij@gmail.com)
Example: ./rejik-stat.py --strip-domain -c PORNO,CHAT,IP -u o.palij,10.6.44.38 -f redirector.log -s IP,vv.palij,10.6.100.2 --html > rejik-stats.html"""

# Main data store - dictionary['user_ip (user_name)'] = { 'category': 'hits', ... }. 'hits' - number of hits to 'category' by 'user_name' from 'user_ip'
db = {}
# data store for categories - dictionary['category'] = 'len'. 'len' - number of rows ranked by 'category' (for plain text view)
categories = {}

domain_re = re.compile(r'^(?P<prefix>.*\\)?(?P<login>[^\\@]*)(?P<suffix>@.*)?$')

def parse_line(line):
    """ Parse one line, return dictionary of 'category', 'user_ip', 'user_name' """
    try:
       line = line.replace('\n','')
       line = line.split()
       category = line[2].replace(':','')
       user_ip = line[3]
       user_name = line[4]
       if options.STRIP_DOMAINS:
          match = domain_re.search(user_name)
          if match:
             user_name = match.group('login')
    except Exception as ex:
       print 'Sorry, it is possible, that log file contain errors: {}'.format(ex)
    else:
       return { 'category': category, 'user_ip': user_ip, 'user_name': user_name.lower() }

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

try:
   fh = open(options.log_file)
except EnvironmentError as ex:
   print >> stderr, 'Problems while opening rejik log file {}: {}'.format(options.log_file, ex)
   exit(1)
else:
   with fh:
      for line in fh:
         stats = parse_line(line)

         if ((stats['user_ip'] in options.USERS) or (stats['user_name'] in options.USERS) or (options.USERS == [])) and \
            ((stats['category'] in options.CATEGORIES) or (options.CATEGORIES == [])) and \
            ((stats['user_ip'] not in options.SKIP) and \
             (stats['user_name'] not in options.SKIP) and \
             (stats['category'] not in options.SKIP)):

            if stats['category'] not in categories:
               length = HITS_ROWS if len(stats['category']) < HITS_ROWS else len(stats['category'])
               categories[ stats['category'] ] = length

            if stats['user_name'] != '-':
               key = "{} ({})".format(stats['user_ip'], stats['user_name'])
            else:
               key = stats['user_ip']
            if key not in db:
               db[key] = {}
            if stats['category'] not in db[key]:
               db[key][ stats['category'] ] = 1
            else:
               db[key][ stats['category'] ] += 1

            if len(key) > NAMES_ROWS:
               NAMES_ROWS = len(key)

# Print title (ips)
field = 'IP (UserName)'
if not options.HTML_OUTPUT:
   print field.ljust(NAMES_ROWS),
else:
   print """<HTML>
 <HEAD>
  <TITLE>
   Rejik Stats
  </TITLE>
 </HEAD>
 <BODY BGCOLOR="#DCDCDC">
  <TABLE BORDER=1 ALIGN=CENTER WIDTH=70%%>
      <tr>
         <td>
           <div STYLE="color: #000080">%s</div>
         </td>"""%(field),

# Print title (categories)
for category, length in sorted(categories.items()):
    if not options.HTML_OUTPUT:
       print category.center(length),
    else:
       print """
         <td ALIGN=CENTER>
           <div STYLE="color: #000080">%s</div>
         </td>"""%(category.center(length)),

if not options.HTML_OUTPUT:
   print
else:
   print """
      </tr>""",

for user, props in db.items():
    if options.HTML_OUTPUT:
       print """ 
      <tr>""",
    # Print report by users
    if not options.HTML_OUTPUT:
       print user.ljust(NAMES_ROWS),
    else:
       print """
         <td>%s</td>"""%(user),

    # Print hists to 'category' for 'user_ip'&'user_name'
    for category, length in sorted(categories.items()):
        hits = props[category] if category in props else 0
        if not options.HTML_OUTPUT:
           print str(hits).center(length),
        else:
           if hits > HITS_HIGHLIGHT:
              hits = """<div STYLE="color: red">%s</div>"""%(hits)
           print """<td ALIGN=CENTER>%s</td>"""%(hits),
    if not options.HTML_OUTPUT:
       print
    else:
       print """
      </tr>""",

if not options.HTML_OUTPUT:
   print
else:
   print """
  </TABLE>
 </BODY>
</HTML>"""

exit(0)

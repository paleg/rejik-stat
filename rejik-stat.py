#!/usr/bin/env python

from __future__ import print_function
import optparse
import sys
import io
import socket

# Minimun numbers of rows in categories (plain text view)
HITS_ROWS = 5
# Minimum numbers of rows in user_ip (user_name) (plain text view)
NAMES_ROWS = 35
# Highlight hits which > then HITS_HIGHLIGHT (html view)
HITS_HIGHLIGHT = 300
# valid sort options
SORTBY_AVAIL = ["hits", "ip"]

def sortby_check(option, opt, value, parser):
   if value not in SORTBY_AVAIL:
      raise optparse.OptionValueError("'{}' is invalid value for 'sortby'. Valid values is {}.".format(value, SORTBY_AVAIL))
   setattr(parser.values, option.dest, value)

USAGE = """$ rejik-stat.py [-h] -f log_file [-d] [--strip-domain] [-c <categories>] [-u <users>]
rejik-stat (Get info in human-readable format from rejik log) by Oleg Palij (mailto,xmpp:o.palij@gmail.com)
Example: ./rejik-stat.py --strip-domain -c PORNO,CHAT,IP -u o.palij,10.6.44.38 -f redirector.log -s IP,vv.palij,10.6.100.2 --html > rejik-stats.html"""

# Main data store - dictionary['user_ip (user_name)'] = { 'category': 'hits', ... }. 'hits' - number of hits to 'category' by 'user_name' from 'user_ip'
db = {}
# data store for categories - dictionary['category'] = 'len'. 'len' - number of rows ranked by 'category' (for plain text view)
categories = {}

def parse_line(line):
    """ Parse one line, return dictionary of 'category', 'user_ip', 'user_name' """
    try:
       line = line.replace('\n','')
       line = line.split()
       category = line[2].replace(':','')
       user_ip = line[3]
       user_name = line[4]
       if options.STRIP_DOMAINS:
          indx = user_name.find("@")
          if indx != -1:
             user_name = user_name[:indx]
          else:
             indx = user_name.find("\\")
             if indx != -1:
                user_name = user_name[indx+1:]
    except Exception as ex:
       print('Sorry, it is possible, that log file contain errors: {}'.format(ex))
    else:
       return { 'category': category, 'user_ip': user_ip, 'user_name': user_name.lower() }

parser = optparse.OptionParser(usage=USAGE)
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
parser.add_option("--sortby",
                     action="callback", callback=sortby_check, type="string", dest="SORTBY", default="hits",
                     help="Sort result table: hits, users [default: %default]")

(options, args) = parser.parse_args()

if options.log_file == None:
   print(USAGE)
   sys.exit(1)

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
   fh = io.open(options.log_file, "tr", errors='replace')
except EnvironmentError as ex:
   print('Problems while opening rejik log file {}: {}'.format(options.log_file, ex), file=sys.stderr)
   sys.exit(1)
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
               categories[ stats['category'] ] = length + 2

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
   print(field.ljust(NAMES_ROWS), end='')
else:
   print("""<HTML>
 <HEAD>
  <TITLE>
   Rejik Stats
  </TITLE>
 </HEAD>
 <BODY BGCOLOR="#DCDCDC">
  <TABLE BORDER=1 ALIGN=CENTER WIDTH=70%>
      <tr>
         <td>
           <div STYLE="color: #000080">{}</div>
         </td>""".format(field), end='')

# Print title (categories)
for category, length in sorted(categories.items()):
    if not options.HTML_OUTPUT:
       print(category.center(length), end='')
    else:
       print("""
         <td ALIGN=CENTER>
           <div STYLE="color: #000080">{}</div>
         </td>""".format(category.center(length)), end='')

if not options.HTML_OUTPUT:
   print()
else:
   print("""
      </tr>""", end='')

sortby = lambda item: -sum(item[1].values())
if options.SORTBY == "ip":
    sortby = lambda item: socket.inet_aton(item[0].split()[0])

for user, props in sorted(db.items(), key=sortby):
    if options.HTML_OUTPUT:
       print("""
      <tr>""", end='')
    # Print report by users
    if not options.HTML_OUTPUT:
       print(user.ljust(NAMES_ROWS), end='')
    else:
       print("""
         <td>{}</td>""".format(user), end='')

    # Print hists to 'category' for 'user_ip'&'user_name'
    for category, length in sorted(categories.items()):
        hits = props[category] if category in props else 0
        if not options.HTML_OUTPUT:
           print(str(hits).center(length), end='')
        else:
           if hits > HITS_HIGHLIGHT:
              hits = """<div STYLE="color: red">{}</div>""".format(hits)
           print("""<td ALIGN=CENTER>{}</td>""".format(hits), end='')
    if not options.HTML_OUTPUT:
       print()
    else:
       print("""
      </tr>""", end='')

if not options.HTML_OUTPUT:
   print()
else:
   print("""
  </TABLE>
 </BODY>
</HTML>""")

sys.exit(0)

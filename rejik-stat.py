#!/usr/local/bin/python

def parse_line(line):
    line = line.replace('\n','')
    line = line.split()
    category = line[2].replace(':','')
    user_ip = line[3]
    user_name = line[4]
    return { 'category': category, 'user_ip': user_ip, 'user_name': user_name }

def get_user_category_hits(db, user_ip, category):
    for i in xrange(0, len(db)):
        if user_ip == db[i]['user_ip'] and category == db[i]['category']:
           return db[i]['hits']
    return 0 

fh = open('redirector.log')

db = []
categoryes = []
user_ips = []

line = fh.readline()
stats = parse_line(line)
db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )
categoryes.append(stats['category'])

while True:
      line = fh.readline()
      if line == '':
         break
      else:
         stats = parse_line(line)

      if stats['category'] not in categoryes:
         categoryes.append(stats['category'])
      if stats['user_ip'] not in user_ips:
         user_ips.append(stats['user_ip'])

      HIT = False

      lenght = len(db)
      for i in xrange(0, lenght):
          if (stats['user_ip'] == db[i]['user_ip']) and (stats['user_name'] == db[i]['user_name']) and (stats['category'] == db[i]['category']):
             HIT = True
             break
      if HIT:
         db[i]['hits'] += 1
      else:
         db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )

fh.close()

print categoryes
for user_ip in user_ips:
    print user_ip,
    for category in categoryes:
        print get_user_category_hits(db, user_ip, category),
    print

#!/usr/local/bin/python

def parse_line(line):
    line = line.replace('\n','')
    line = line.split()
    category = line[2].replace(':','')
    user_ip = line[3]
    user_name = line[4]
    return { 'category': category, 'user_ip': user_ip, 'user_name': user_name }

fh = open('redirector.log')

db = []

line = fh.readline()
stats = parse_line(line)
db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )

while True:
      line = fh.readline()
      if line == '':
         break
      else:
         stats = parse_line(line)

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

for i in xrange(0, lenght):
    print db[i]

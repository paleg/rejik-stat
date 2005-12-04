#!/usr/local/bin/python
HITS_ROWS = 5
NAMES_ROWS = 30

def parse_line(line):
    line = line.replace('\n','')
    line = line.split()
    category = line[2].replace(':','')
    user_ip = line[3]
    user_name = line[4]
    return { 'category': category, 'user_ip': user_ip, 'user_name': user_name }

def get_user_category_hits(db, user_ip, user_name, category):
    for i in xrange(0, len(db)):
        if (user_ip == db[i]['user_ip']) and (user_name == db[i]['user_name']) and(category == db[i]['category']):
           return db[i]['hits']
    return 0 

fh = open('redirector.log')

db = []
categoryes = []
users = []

line = fh.readline()
stats = parse_line(line)
db.append( { 'user_ip': stats['user_ip'], 'user_name':stats['user_name'], 'category': stats['category'], 'hits': 1 } )
categoryes.append({ 'category': stats['category'], 'len': len(stats['category']) } )
users.append( { 'user_ip': stats['user_ip'], 'user_name': stats['user_name'] } )

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

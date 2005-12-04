#!/usr/local/bin/python

def parse_line(line):
    line = line.split()
    date_time = line[0] + ' ' + line[1]
    category = line[2].replace(':','')
    user_ip = line[3]
    user_name = line[4]
    url = line[5]
    return { 'logTime': date_time, 'category': category, 'user_ip': user_ip, 'user_name': user_name, 'url': url }

fh = open('redirector.log')

line = fh.readline()
users = []
user_ips = []
categoryes = []

while line != '':
      stats = parse_line(line)
      if stats['user_ip'] not in user_ips:
         user_ips.append(stats['user_ip'])
      if stats['user_name'] not in users:
         users.append(stats['user_name']
      if stats['category'] not in categoryes:
         categoryes.append(stats['category']
      line = line.replace('\n','')
      line = fh.readline()

fh.close()

print categoryes

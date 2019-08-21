# -*- coding: utf-8 -*-

hstr = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: zjip.patsev.com
Referer: http://zjip.patsev.com/pldb-zj/
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'''

header = dict()
for i in hstr.split('\n'):
  ind = i.find(':')
  k = i[:ind]
  v = i[ind + 1:].strip()
  header[k] = v

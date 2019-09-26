# -*- coding: utf-8 -*-
import requests
from pymongo import MongoClient
import random

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']
# proxy_col.drop()

# chrome cookie
# chrome://settings/siteData?search=cookie

# proxy url
# http://h.jiguangdaili.com/api/new_api.html
# jghttp335911
headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding':
        'gzip, deflate',
    'Accept-Language':
        'zh-CN,zh;q=0.9',
    'Connection':
        'keep-alive',
    # removed because it confuses requests redirect mechanism
    # 'Host':
    #     'zjip.patsev.com',
    # 'Referer':
    #     'http://zjip.patsev.com/pldb-zj/',
    'Upgrade-Insecure-Requests':
        '1',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Purpose':
        'prefetch'
}

res_hist_dict = dict()
sess = requests.Session()


def make_query(url, name, red=True, proxy=True):
  ip_port_dict = random.choice(list(proxy_col.find()))
  proxy_dict = {
      'http': 'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port'])
  }
  if proxy:
    res = sess.get(
        url, proxies=proxy_dict, headers=headers, allow_redirects=red)
  else:
    res = sess.get(url, headers=headers, allow_redirects=red)
  res_hist_dict[url] = [name, res]
  print(res.text[:100])
  with open(name + '.html', 'w') as f:
    f.writelines(res.text)
  return res


url = 'http://zjip.patsev.com/'
name = '1'
res = make_query(url, name)

url = 'http://zjip.patsev.com/pldb-zj/' + 'access/toLogin'
name = '2'
res = make_query(url, name, red=False)

url = res.headers['Location']
name = '3'
# res = make_query(url, name, red=False, proxy=False)
res = make_query(url, name, red=False)


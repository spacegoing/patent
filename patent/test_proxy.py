# -*- coding: utf-8 -*-
import requests
from pymongo import MongoClient
import random
# chrome cookie
# chrome://settings/siteData?search=cookie

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']
# proxy_col.drop()

# proxy url
# http://h.jiguangdaili.com/api/new_api.html
# jghttp335911
# url = 'http://zjip.patsev.com/'
url = 'http://httpbin.org/ip'
# url = 'http://open.cnipr.com/oauth/authorize?client_id=8A3C47AC471F1D588A0F84B93E540C06&response_type=code&redirect_uri=http://zjip.patsev.com/pldb-zj/access/oauthLogin'

headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding':
        'gzip, deflate',
    'Accept-Language':
        'zh-CN,zh;q=0.9',
    'Connection':
        'keep-alive',
    'Host':
        'zjip.patsev.com',
    'Referer':
        'http://zjip.patsev.com/pldb-zj/',
    'Upgrade-Insecure-Requests':
        '1',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Purpose':
        'prefetch'
}

ip_port_dict = random.choice(list(proxy_col.find()))
proxy_dict = {
    'http': 'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port'])
}

res = requests.get(url, proxies=proxy_dict, headers=headers)
# res = requests.get(url, headers=headers)
print(res.text[:100])

with open('test.html', 'w') as f:
  f.writelines(res.text)

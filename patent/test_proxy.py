# -*- coding: utf-8 -*-
import requests

# url = 'http://115.238.84.42:8081/frmLogin.aspx'
url = 'http://zjip.patsev.com/'
# jghttp335911
# url = 'http://httpbin.org/ip'
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
proxy_dict = {'http': 'http://36.34.27.76:4554'}
res = requests.get(url, proxies=proxy_dict, headers=headers)
print(res.text[:100])
# res = requests.get(url, headers=headers)

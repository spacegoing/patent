# -*- coding: utf-8 -*-
import requests
from pymongo import MongoClient
import random
from urllib import parse
from shadow_useragent import ShadowUserAgent as ua

debug = True
if debug:
  res_hist_dict = dict()

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']
# proxy_col.drop()

# chrome cookie
# chrome://settings/siteData?search=cookie

# proxy url
# http://h.jiguangdaili.com/api/new_api.html
# jghttp335911
agent = ua().random
headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding':
        'gzip, deflate',
    'Accept-Language':
        'zh-CN,zh;q=0.9',
    # 'Connection':
    #     'keep-alive',
    # removed because it confuses requests redirect mechanism
    # 'Host':
    #     'zjip.patsev.com',
    # 'Referer':
    #     'http://zjip.patsev.com/pldb-zj/',
    # 'Upgrade-Insecure-Requests':
    #     '1',
    'User-Agent':
        agent,
    # 'Purpose':
    #     'prefetch'
}

sess = requests.Session()
sess.headers.update(headers)


def make_query(url, name, red=True, proxy=True):
  ip_port_dict = random.choice(list(proxy_col.find()))
  proxy_dict = {
      'http': 'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port'])
  }
  if proxy:
    res = sess.get(url, proxies=proxy_dict, allow_redirects=red)
  else:
    res = sess.get(url, allow_redirects=red)
  if debug:
    res_hist_dict[url] = [name, res]
    with open(name + '.html', 'w') as f:
      f.writelines(res.text)
  return res


def login(cnipr_res, proxy=True):
  client_id = parse.parse_qs(parse.urlsplit(
      cnipr_res.url).query)['client_id'][0]
  form_data = {
      'userName': 'spacebnbk',
      'password': 'QWertyuio123',
      'clientId': client_id,
      'responseType': 'code',
      'redirectUri': 'http://zjip.patsev.com/pldb-zj/access/oauthLogin',
      'state': ''
  }
  ip_port_dict = random.choice(list(proxy_col.find()))
  proxy_dict = {
      'http': 'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port'])
  }
  if proxy:
    res = sess.post(
        'http://open.cnipr.com/oauth/json/authorize',
        proxies=proxy_dict,
        headers=headers,
        data=form_data)
  else:
    res = sess.post(
        'http://open.cnipr.com/oauth/json/authorize',
        data=form_data,
        headers=headers)
  if debug:
    res_hist_dict['login'] = ['login', res]
    print(res.text[:100])
    with open('login' + '.html', 'w') as f:
      f.writelines(res.text)
  url = res.json()['message']
  return url


url = 'http://zjip.patsev.com/'
name = '1'
res = make_query(url, name)

url = 'http://zjip.patsev.com/pldb-zj/' + 'access/toLogin'
name = '2'
res = make_query(url, name, red=False)

url = res.headers['Location']
name = '3'
# res = make_query(url, name, red=False, proxy=False)
cnipr_res = make_query(url, name, red=False)
print(len(cnipr_res.text))

logined_url = login(cnipr_res)

ip_port_dict = random.choice(list(proxy_col.find()))
proxy_dict = {
    'http': 'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port'])
}
logined_res = sess.get(logined_url, proxies=proxy_dict)
with open('login' + '.html', 'w') as f:
  f.writelines(logined_res.text)

no_per_page = 30
pat_form_data = {
    'dbs': 'FMZL,SYXX,WGZL,FMSQ',
    'displayCols': '',
    'exp': "(申请日= (1990 to 2019)) AND (申请人类型=('工矿企业'))",
    'from': '1',
    'isSimilar': 'false',
    'option': '',
    'order': '',
    'size': str(no_per_page)
}
pat_query_url='http://zjip.patsev.com//pldb-zj/access/hostingplatform/search/patent/route/patent-overview'
pat_query_res = sess.post(pat_query_url, proxies=proxy_dict, data=pat_form_data)

with open('pat' + '.html', 'w') as f:
  f.writelines(pat_query_res.text)

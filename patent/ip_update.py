# -*- coding: utf-8 -*-
import time
import datetime
import requests
import dateparser as dp
import pytz
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']


def insert_proxy(proxy_list):
  proxy_col.insert_many(proxy_list)


def get_ip_list(num):
  '''
  required by tiqu.qingjuhe.cn, the num should less than 500
  '''

  tmp_url = 'http://http.tiqu.qingjuhe.cn/getip?num=%d&type=2&pack=34807&port=11&ts=1&lb=1&pb=45&regions='
  url = (tmp_url % (num))

  def get_ip(url):
    resp = requests.get(url)
    json_data = resp.json(
    )  # Check the JSON Response Content documentation below
    return json_data

  while True:
    time.sleep(2)
    json_data = get_ip(url)
    print('Query IP proxies, status: %s' % json_data['success'])
    if json_data['success']:
      ip_list = json_data['data']
      return ip_list


def update_ip_list():
  try:
    bjtz = pytz.timezone('Asia/Shanghai')
    sydtz = pytz.timezone('Australia/Sydney')

    to_remove_list = []
    for i in proxy_col.find():
      exp_time = dp.parse(
          i['expire_time'],
          date_formats=['%Y-%m-%d %H:%M:%S']).replace(tzinfo=bjtz)
      now = datetime.datetime.now().replace(tzinfo=sydtz)
      if time.localtime().tm_isdst:
        now = now + datetime.timedelta(hours=-1)
      secs = (exp_time - now).total_seconds()
      if secs < 10:
        print("Expired IP Address: ")
        print(i)
        print(exp_time)
        print(now)
        print(secs)
        to_remove_list.append(i)

    res = proxy_col.delete_many({
        '_id': {
            '$in': [i['_id'] for i in to_remove_list]
        }
    })
    num = res.deleted_count
    if num != len(to_remove_list):
      import ipdb
      ipdb.set_trace(context=7)

    # insert new ips
    if num:
      print("Deleted :")
      for i in to_remove_list:
        print(i)
      ip_list = get_ip_list(num)
      print("Insert " + str(ip_list))
      insert_proxy(ip_list)
  except:
    import ipdb
    ipdb.set_trace(context=7)


if __name__ == "__main__":
  insert_proxy(get_ip_list(20))
  time.sleep(2)
  while True:
    update_ip_list()
    time.sleep(5)

  # def get_proxy_list():
  #   proxy_list = [
  #       'http://%s:%s' % (str(i['ip']), str(i['port'])) for i in proxy_col.find()
  #   ]
  #   return proxy_list

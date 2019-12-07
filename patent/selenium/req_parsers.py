# -*- coding: utf-8 -*-
import time
import requests
from requests_futures.sessions import FuturesSession
from shadow_useragent import ShadowUserAgent as ua
# selenium
from selenium import webdriver
# Custom Packs
from login import login

# urls
query_patent_list_url = 'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/load-patent-overview'

# params
item_per_page = 30


# util functions
def get_random_header():
  header = {
      'Accept':
          '*/*',
      'Accept-Encoding':
          'gzip, deflate',
      'Accept-Language':
          'en-US,en;q=0.9',
      'Connection':
          'keep-alive',
      'Host':
          'zjip.patsev.com',
      'User-Agent':
          ua().random,
      'Origin':
          'http://zjip.patsev.com',
      'Referer':
          'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/route/patent-overview',
      'X-Requested-With':
          'XMLHttpRequest'
  }
  return header


def set_sess_cookie(driver, sess):
  cookie = driver.get_cookies()[0]
  tmp_cookie = {
      'domain': 'zjip.patsev.com',
      'rest': {
          'httpOnly': True
      },
      'path': '/pldb-zj',
      'secure': False
  }
  req_cookie = requests.cookies.create_cookie(cookie['name'], cookie['value'],
                                              **tmp_cookie)
  sess.cookies.set_cookie(req_cookie)


def create_form_data(page_no):
  form_data = {
      'dbs': 'FMZL,SYXX,WGZL,FMSQ',
      'displayCols': '',
      'exp': "(申请日= (1990 to 2019)) AND (申请人类型=('工矿企业'))",
      'from': str(page_no),
      'isSimilar': 'false',
      'option': '',
      'order': '',
      'size': str(item_per_page)
  }
  task_form_dict = dict()
  for k, v in form_data.items():
    task_form_dict[k] = (None, v)
  return task_form_dict


# https queries
def get_total_items_pages(sess):
  # query patent list page 1, only to get total pages
  form_data = create_form_data(1)
  header = get_random_header()
  future = sess.post(query_patent_list_url, headers=header, files=form_data)
  res = future.result()
  total_items = res.json()['total']
  # from searchForm page (patent list page) js script
  total_pages = total_items // item_per_page
  if total_items % item_per_page:
    total_pages += 1
  return total_items, total_pages


options = webdriver.ChromeOptions()
driver = webdriver.Chrome('./chromedriver', options=options)
sess = FuturesSession()

login(driver)
set_sess_cookie(driver, sess)
total_items, total_pages = get_total_items_pages(sess)
print('total pages: ', total_pages)

pages_per_min = 15
total_page_num_list = list(range(1, total_pages + 1))

# main loop
for i in total_page_num_list[::pages_per_min]:
  # scrape pages_per_min pages per minute
  page_num_list = total_page_num_list[i:i + pages_per_min]

  # start scraping
  start_time = time.time()
  for num in page_num_list:
    break

  # wait at least 1 minute
  if time.time() - start_time < 60:
    time.sleep(time.time() - start_time)

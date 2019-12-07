# -*- coding: utf-8 -*-
from urllib.parse import urljoin
# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
# todo:UI
from selenium.webdriver.support.ui import WebDriverWait

zjip_url = "http://zjip.patsev.com/"


def login(driver):
  # get login page
  # todo:UI
  wait = WebDriverWait(driver, 10)
  driver.get(zjip_url)
  wait.until(
      presence_of_element_located((By.CSS_SELECTOR, "div.reg-auth-form")))

  # submit user pass form
  # there are two forms, one real form, another display=None
  # use the first one (real one)
  input_list = driver.find_elements_by_xpath('//form//input')
  real_user_el = input_list[0]
  real_pass_el = input_list[1]
  real_user_el.send_keys('spacebnbk')
  real_pass_el.send_keys('QWertyuio123')
  button_list = driver.find_elements_by_xpath('//form//button')
  real_button_el = button_list[0]
  real_button_el.click()
  wait.until(presence_of_element_located((By.CSS_SELECTOR, "div.power-search")))


def print_el_list_attrs(el_list):
  # print tag's attributes=value
  # el_list = driver.find_elements_by_xpath('//form//button')
  for e in el_list:
    print('---------')
    print('text: ', e.text)
    for node in e.get_property('attributes'):
      print(node['nodeName'], '=', node['nodeValue'])


options = webdriver.ChromeOptions()
driver = webdriver.Chrome('./chromedriver', options=options)
# with webdriver.Chrome('./chromedriver', options=options) as driver:
login(driver)
driver.get(
    urljoin(zjip_url, '/pldb-zj/route/hostingplatform/search/searchForm'))

import requests

cookie = driver.get_cookies()[0]
tmp_cookie = {
    'domain': 'zjip.patsev.com',
    'rest': {
        'httpOnly': True
    },
    'path': '/pldb-zj',
    'secure': False
}

sess = requests.Session()
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
      'size': '30'
  }
  task_form_dict = dict()
  for k,v in form_data.items():
    task_form_dict[k] = (None, v)
  return task_form_dict

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
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'Origin':
        'http://zjip.patsev.com',
    'Referer':
        'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/route/patent-overview',
    'X-Requested-With':
        'XMLHttpRequest'
}

patent_list_url = 'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/load-patent-overview'
form_data = create_form_data(1)
res = sess.post(
    patent_list_url, headers=header, files=form_data)

with open('pat_list.html', 'w') as f:
  f.write(res.text)

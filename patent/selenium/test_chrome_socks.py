# -*- coding: utf-8 -*-
import random
import json
import requests
from bs4 import BeautifulSoup
import dateparser as dp
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
# chrome cookie
# chrome://settings/siteData?search=cookie

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']

# proxy_col.drop()


def get_driver():
  ip_port_dict = random.choice(list(proxy_col.find()))
  expire_time = dp.parse(
      ip_port_dict['expire_time'], date_formats=['%Y-%m-%d %H:%M:%S'])
  print(ip_port_dict)
  options = webdriver.ChromeOptions()
  socks_str = "--proxy-server=socks5://" + ip_port_dict['ip'] \
                               + ":" + ip_port_dict['port']
  map_str = '--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE ' + ip_port_dict['ip'] + '"'
  options.add_argument(socks_str)
  options.add_argument(map_str)
  driver = webdriver.Chrome('./chromedriver', options=options)
  return driver, expire_time


driver, expire_time = get_driver()
driver.get('https://www.showmyip.gr')

url = 'zjip.patsev.com'

name_list = list()
with open('stock_list.csv', 'w') as f:
  for i, s in enumerate(sec_list):
    print(i)
    try:
      driver.get(url % s)
      myElem = WebDriverWait(driver, 30).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,
                                          'widget-stocks-header')))
      cname = myElem.find_element_by_class_name(
          'widget-stocks-header-title').text
      b, m, e = cname.find('('), cname.find('/'), cname.find(')')
      name = cname[:b].strip()
      code = s
      ric = cname[m + 1:e].strip()
      tags_cont = myElem.find_element_by_class_name(
          'widget-stocks-header-tags-container').find_elements_by_class_name(
              'website-tag')
      industry_list = [t.text for t in tags_cont]
      cname_str = ','.join([name, code, ric] + industry_list)
      f.write(cname_str + '\n')
    except:
      print(url % s)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

#This example requires Selenium WebDriver 3.13 or newer
with webdriver.Firefox() as driver:
  wait = WebDriverWait(driver, 10)
  driver.get("https://google.com/ncr")
  driver.find_element_by_name("q").send_keys("cheese" + Keys.RETURN)
  first_result = wait.until(
      presence_of_element_located((By.CSS_SELECTOR, "h3>div")))
  print(first_result.get_attribute("textContent"))

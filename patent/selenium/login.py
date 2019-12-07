# -*- coding: utf-8 -*-
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


if __name__ == "__main__":
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome('./chromedriver', options=options)
  login(driver)

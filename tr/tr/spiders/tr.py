# -*- coding: utf-8 -*-
import json
import scrapy
import dateparser as dp
from urllib import parse
import xlrd
import pandas as pd
import traceback
from pymongo import MongoClient
import random

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']
DEBUG = False


class InnerException(Exception):
  '''
  workaround for inner exception of parse_insert_comment
  only for parse_post_page to use to keep raising
  exception as i.args[0]

  some unregistered user will cause user_name.strip()
  NoneType error
  Ignore those users / comments / posts
  '''
  pass


class PatentSpider(scrapy.Spider):
  '''
  yield_dict: mandantory keys
    db_handler
    meta_dict
    error
    result
  '''
  name = 'tr'

  def __init__(self):
    super().__init__()

    # flags' dict for determing whether keep scraping
    self.comment_cont_dict = dict()
    self.post_cont_dict = dict()
    self.no_per_page = 30
    self.max_old_num = 5
    self.stop_date_flag = dp.parse('2018-12-31')
    self.scrapy_meta_keys = [
        'depth', 'download_timeout', 'download_slot', 'download_latency', '_id'
    ]
    # this is from downloaded excel by function xls_query()
    self.xls_column_names = [
        '申请号', '申请日', '公开（公告）号', '公开（公告）日', '申请（专利权）人', '发明（设计）人', '分类号', '优先权',
        '专利代理机构', '代理人', '国际申请', '国际公布', '进入国家日期', '摘要', '地址', '名称', '专利同族',
        '专利引证', '最新法律状态', '法律状态', '专利权状态'
    ]
    self.xls_column_names_en = []

  def start_requests(self):
    # cnipr 13601137085
    headers = {
        'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding':
            'gzip, deflate',
        'Accept-Language':
            'zh-CN,zh;q=0.9',
        'Referer':
            'http://zjip.patsev.com/pldb-zj/',
        'DNT':
            1,
        'Upgrade-Insecure-Requests':
            '1',
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    ip_port_dict = random.choice(list(proxy_col.find()))
    yield scrapy.Request(
        url='http://zjip.patsev.com/',
        headers=headers,
        callback=self.login,
        dont_filter=True,
        meta={
            'proxy':
                'http://%s:%s' % (ip_port_dict['ip'], ip_port_dict['port']),
            # 'dont_redirect': True
        })
    # yield scrapy.Request(
    #     url='http://httpbin.org/ip',
    #     headers=headers,
    #     callback=self.login,
    #     dont_filter=True,
    #     meta={'proxy': 'http://49.87.29.120:4573'})

  def login(self, response):
    from scrapy.shell import inspect_response
    inspect_response(response, self)
    # import ipdb
    # ipdb.set_trace(context=7)
    client_id = parse.parse_qs(parse.urlsplit(
        response.url).query)['client_id'][0]

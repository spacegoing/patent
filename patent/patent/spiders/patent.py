# -*- coding: utf-8 -*-
import json
import scrapy
import dateparser as dp
from urllib import parse
import xlrd
import pandas as pd
import traceback

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
  name = 'patent'

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
    yield scrapy.Request(
        url='http://zjip.patsev.com', callback=self.login, dont_filter=True)

  def login(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    client_id = parse.parse_qs(parse.urlsplit(
        response.url).query)['client_id'][0]
    form_data = {
        'userName': 'spacebnbk',
        'password': 'QWertyuio123',
        'clientId': client_id,
        'responseType': 'code',
        'redirectUri': 'http://zjip.patsev.com/pldb-zj/access/oauthLogin',
        'state': ''
    }
    yield scrapy.FormRequest(
        url='http://open.cnipr.com/oauth/json/authorize',
        formdata=form_data,
        callback=self.login_redirect,
        dont_filter=True)

  def login_redirect(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    # this url contains openkey openid etc
    url = json.loads(response.text)['message']
    yield scrapy.Request(
        url=url, callback=self.request_search_form, dont_filter=True)

  def request_search_form(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    form_data = {
        'dbs': 'FMZL,SYXX,WGZL,FMSQ',
        'displayCols': '',
        'exp': "(申请日= (1990 to 2019)) AND (申请人类型=('工矿企业'))",
        'from': '1',
        'isSimilar': 'false',
        'option': '',
        'order': '',
        'size': str(self.no_per_page)
    }
    yield scrapy.FormRequest(
        url=
        'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/load-patent-overview',
        formdata=form_data,
        callback=self.first_result_page_parser,
        dont_filter=True)

  def first_result_page_parser(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    json_returned = json.loads(response.text)
    total_pages = json_returned['total'] // 30
    if json_returned['total'] % 30:
      total_pages += 1

    json_returned = json.loads(response.text)
    result_list = json_returned['results']
    pid_list = [i['pid'] for i in result_list]
    pid_str = ','.join(pid_list)
    field_str = '申请号,申请日,公开（公告）号,公开（公告）日,申请（专利权）人,发明（设计）人,分类号,优先权,专利代理机构,代理人,国际申请,国际公布,进入国家日期,摘要,地址,名称,专利同族,专利引证,最新法律状态,法律状态,专利权状态'
    form_data = {'bibFields': field_str, 'selectedPatentList': pid_str}

    meta_dict = {'query_result_list': result_list, 'from_index': 1}
    yield scrapy.FormRequest(
        url=
        'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/download/bib',
        formdata=form_data,
        callback=self.xls_query,
        dont_filter=True,
        meta=meta_dict,
        priority=20)

    # following pagination pages
    self.logger.info('Total Pages: %d' % total_pages)
    for i in range(2, total_pages + 1):
      form_data = {
          'dbs': 'FMZL,SYXX,WGZL,FMSQ',
          'displayCols': '',
          'exp': "(申请日= (1990 to 2019)) AND (申请人类型=('工矿企业'))",
          'from': str(i),
          'isSimilar': 'false',
          'option': '',
          'order': '',
          'size': str(self.no_per_page)
      }
      yield scrapy.FormRequest(
          url=
          'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/load-patent-overview',
          formdata=form_data,
          callback=self.parse_search_form_json,
          dont_filter=True,
          priority=20)

  def parse_search_form_json(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    db_handler = ''
    yield_dict = {
        'error': False,
        'db_handler': db_handler,
        'meta_dict': self.get_meta(response)
    }

    try:
      json_returned = json.loads(response.text)
      result_list = json_returned['results']
      pid_list = [i['pid'] for i in result_list]
      pid_str = ','.join(pid_list)
      field_str = '申请号,申请日,公开（公告）号,公开（公告）日,申请（专利权）人,发明（设计）人,分类号,优先权,专利代理机构,代理人,国际申请,国际公布,进入国家日期,摘要,地址,名称,专利同族,专利引证,最新法律状态,法律状态,专利权状态'
      form_data = {'bibFields': field_str, 'selectedPatentList': pid_str}

      form_str_list = [
          i.strip()
          for i in response.request.body.decode('utf-8').split('&')
          if 'from' in i
      ]
      from_index = int(form_str_list[0][5:])
      self.logger.info('Scraping page: %d' % from_index)
      meta_dict = {'query_result_list': result_list, 'from_index': from_index}
      yield scrapy.FormRequest(
          url=
          'http://zjip.patsev.com/pldb-zj/access/hostingplatform/search/patent/json/download/bib',
          formdata=form_data,
          callback=self.xls_query,
          dont_filter=True,
          meta=meta_dict,
          priority=30)

      yield_dict['result'] = {'from_index': from_index}
      yield_dict['db_handler'] = 'insert_scrapped_page_index'
      yield_dict['meta_dict'] = meta_dict
      yield yield_dict
    except Exception as e:
      yield_dict['from_index_request_headers'] = response.request.body.decode(
          'utf-8')
      yield_dict = self.get_except_yield_dict(e, yield_dict, response)
      yield yield_dict

  def xls_query(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    db_handler = ''
    yield_dict = {
        'error': False,
        'db_handler': db_handler,
        'meta_dict': self.get_meta(response)
    }
    try:
      url = json.loads(response.text)['fileName']
      url = 'http://zjip.patsev.com/pldb-zj/fileTemp/' + url
      yield scrapy.Request(
          url,
          callback=self.xls_parser,
          meta=self.get_meta(response),
          dont_filter=True,
          priority=40)
    except Exception as e:
      yield_dict = self.get_except_yield_dict(e, yield_dict, response)
      yield yield_dict

  def xls_parser(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    db_handler = 'insert_result_list'
    yield_dict = {
        'error': False,
        'db_handler': db_handler,
        'meta_dict': self.get_meta(response)
    }

    try:
      book = xlrd.open_workbook(
          file_contents=response.body, encoding_override='gb2312')
      df = pd.read_excel(book)
      indices = [2, 10, 11, 12, 16]
      # key_names = ['公开（公告）号', '国际申请', '国际公布', '进入国家日期', '专利同族']
      key_maps = ['pubNumber', 'iapp', 'ipub', 'den', 'family']
      tdf = df.iloc[:, indices]
      tdf.columns = key_maps
      for d, td in zip(
          response.meta['query_result_list'], tdf.to_dict(orient='record')):
        if d['pubNumber'] != td['pubNumber']:
          raise Exception(
              'Downloaded Excel and Weblist items are in different order')
        d.update(td)
      yield_dict['result'] = {
          'query_result_list': response.meta['query_result_list']
      }
      yield yield_dict
    except Exception as e:
      yield_dict = self.get_except_yield_dict(e, yield_dict, response)
      yield yield_dict

  def get_meta(self, response):
    meta = {
        k: v
        for k, v in response.meta.items()
        if k not in self.scrapy_meta_keys
    }
    return meta

  def get_except_yield_dict(self, e, yield_dict, response):
    yield_dict['error'] = {
        'error_message': '%s: %s' % (e.__class__, str(e)),
        'traceback': traceback.format_exc(),
        'url': response.url
    }
    yield_dict['db_handler'] = 'error_insert'
    return yield_dict

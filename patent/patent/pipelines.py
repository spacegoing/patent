# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import traceback
import dateparser as dp

client = MongoClient('mongodb://localhost:27017/')
patent_db = client['patent_db']
patent_col = patent_db['patent_col']
error_col = patent_db['error']


def parse_type(patType, dbName):
  patent_type = ''
  if patType == 1:
    if dbName == 'FMZL':
      patent_type = '发明公开'
    else:
      patent_type = '发明授权'
  elif patType == 2:
    patent_type = '实用新型'
  elif patType == 3:
    patent_type = '外观专利'
  elif patType == 8:
    if dbName == 'FMZL':
      patent_type = '发明公开'
    else:
      patent_type = '发明授权'
  elif patType == 9:
    patent_type = '实用新型'
  return patent_type


def parse_status(statusCode):
  legalStatus = ''
  if statusCode == 10:
    legalStatus = '有效专利'
  elif statusCode == 20:
    legalStatus = '失效专利'
  elif statusCode == 21:
    legalStatus = '专利权届满的专利'
  elif statusCode == 22:
    legalStatus = '在审超期'
  elif statusCode == 30:
    legalStatus = '在审专利'
  return legalStatus


def parse_citation_list(citationInfo):
  citation_list = []
  if citationInfo:
    citation_list = [i['citationInfoNo'][0] for i in citationInfo]
  return citation_list


def parse_dict_date(d):

  def parse_date(date):
    return dp.parse(date, date_formats=['%Y.%m.%d'])

  keys = ['appDate', 'pubDate', 'priorityDate', 'issueDate']
  for k in keys:
    if d[k]:
      d[k] = parse_date(d[k])


def get_except_yield_dict(e, i):
  yield_dict = {
      'error_message': '%s: %s' % (e.__class__, str(e)),
      'traceback': traceback.format_exc(),
      'patent_dict': i
  }
  yield_dict['db_handler'] = 'error_insert'
  return yield_dict


class PatentPipeline(object):

  def process_item(self, item, spider):
    for i in item['query_result_list']:
      try:
        patent_type = parse_type(int(i['patType']), i['dbName'])
        legal_status = parse_status(int(i['statusCode']))
        citation_list = parse_citation_list(i['citationInfo'])
        i.update({
            'patentType': patent_type,
            'legalStatus': legal_status,
            'citationList': citation_list
        })
        parse_dict_date(i)
      except Exception as e:
        except_dict = get_except_yield_dict(e, i)
        error_col.insert_one(except_dict)

    patent_col.insert_many(item['query_result_list'])
    return item

# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
# For proxy middleware
import random
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
proxy_db = client['Patent_Proxy']
proxy_col = proxy_db['Proxy']


class PatentSpiderMiddleware(object):
  # Not all methods need to be defined. If a method is not defined,
  # scrapy acts as if the spider middleware does not modify the
  # passed objects.

  @classmethod
  def from_crawler(cls, crawler):
    # This method is used by Scrapy to create your spiders.
    s = cls()
    crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
    return s

  def process_spider_input(self, response, spider):
    # Called for each response that goes through the spider
    # middleware and into the spider.

    # Should return None or raise an exception.
    return None

  def process_spider_output(self, response, result, spider):
    # Called with the results returned from the Spider, after
    # it has processed the response.

    # Must return an iterable of Request, dict or Item objects.
    for i in result:
      yield i

  def process_spider_exception(self, response, exception, spider):
    # Called when a spider or process_spider_input() method
    # (from other spider middleware) raises an exception.

    # Should return either None or an iterable of Response, dict
    # or Item objects.
    pass

  def process_start_requests(self, start_requests, spider):
    # Called with the start requests of the spider, and works
    # similarly to the process_spider_output() method, except
    # that it doesn’t have a response associated.

    # Must return only requests (not items).
    for r in start_requests:
      yield r

  def spider_opened(self, spider):
    spider.logger.info('Spider opened: %s' % spider.name)


class PatentDownloaderMiddleware(object):
  # Not all methods need to be defined. If a method is not defined,
  # scrapy acts as if the downloader middleware does not modify the
  # passed objects.

  @classmethod
  def from_crawler(cls, crawler):
    # This method is used by Scrapy to create your spiders.
    s = cls()
    crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
    return s

  def process_request(self, request, spider):
    # Called for each request that goes through the downloader
    # middleware.

    # Must either:
    # - return None: continue processing this request
    # - or return a Response object
    # - or return a Request object
    # - or raise IgnoreRequest: process_exception() methods of
    #   installed downloader middleware will be called
    return None

  def process_response(self, request, response, spider):
    # Called with the response returned from the downloader.

    # Must either;
    # - return a Response object
    # - return a Request object
    # - or raise IgnoreRequest
    return response

  def process_exception(self, request, exception, spider):
    # Called when a download handler or a process_request()
    # (from other downloader middleware) raises an exception.

    # Must either:
    # - return None: continue processing this exception
    # - return a Response object: stops process_exception() chain
    # - return a Request object: stops process_exception() chain
    pass

  def spider_opened(self, spider):
    spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):

  def __init__(self, settings):

    fallback = settings.get('FAKEUSERAGENT_FALLBACK', None)
    self.ua = UserAgent(fallback=fallback)
    self.per_proxy = settings.get('RANDOM_UA_PER_PROXY', False)
    self.ua_type = settings.get('RANDOM_UA_TYPE', 'random')
    self.proxy2ua = {}

  @classmethod
  def from_crawler(cls, crawler):
    return cls(crawler.settings)

  def process_request(self, request, spider):

    def get_ua():
      '''Gets random UA based on the type setting (random, firefox…)'''
      return getattr(self.ua, self.ua_type)

    if self.per_proxy:
      proxy = request.meta.get('proxy')
      if proxy not in self.proxy2ua:
        self.proxy2ua[proxy] = get_ua()
        spider.logger.debug('Assign User-Agent %s to Proxy %s' %
                            (self.proxy2ua[proxy], proxy))
      request.headers.setdefault('User-Agent', self.proxy2ua[proxy])
    else:
      request.headers.setdefault('User-Agent', get_ua())


class RandomProxy(object):

  def __init__(self, settings):
    pass

  @classmethod
  def from_crawler(cls, crawler):
    return cls(crawler.settings)

  def process_request(self, request, spider):
    # Don't overwrite with a random one (server-side state for IP)
    if 'proxy' in request.meta:
      if request.meta["exception"] is False:
        return
    request.meta["exception"] = False
    proxy_address = random.choice(list(proxy_col.find()))
    request.meta[
        'proxy'] = 'http://' + proxy_address['ip'] + ':' + proxy_address['port']

  def process_response(self, request, response, spider):
    # Called with the response returned from the downloader.

    # Must either;
    # - return a Response object
    # - return a Request object
    # - or raise IgnoreRequest
    # import ipdb
    # ipdb.set_trace(context=7)
    return response

  def process_exception(self, request, exception, spider):
    if 'proxy' not in request.meta:
      return
    http, proxy_ip, proxy_port = request.meta['proxy'].split(':')
    proxy_ip = proxy_ip[2:] # :// in url, exclude // here
    import ipdb
    ipdb.set_trace(context=7)
    proxy_col.delete_many({'ip': proxy_ip, 'port': proxy_port})
    # if 'timeout' or 'connectionlost' in str(exception).lower():
    #   request.meta['dont_retry'] = True
    # delete from database
    spider.logger.info('Removing failed proxy <%s>, %d proxies left' %
                       (proxy_ip, proxy_col.count()))

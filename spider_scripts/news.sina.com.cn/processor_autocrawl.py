#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-02-03 15:23:32
#
#target address:
#  http://s.weibo.com/top/summary?cate=realtimehot
#

from pyspider.libs.base_handler import *
from datetime import timedelta, datetime
from log.logger import *
import time
from core.textrank import textrank
from core.simhash import simhash
from header_switch import HeadersSelector

logger = getLogger("s.weibo.com")

class Handler(BaseHandler):
    crawl_config = {
        "user_agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "timeout": 20,
        "connect_timeout": 10,
        "retries": 3,
        "fetch_type": 'None',
        "auto_recrawl": False,
    }

    #   address
    _address = 'http://news.sina.com.cn/hotnews/'

    def get_taskid(self, task):
        return task['url']

    @config(priority=3)
    def on_start(self):
        '''
        seeds .
        fetching news
        will calliing the next_page function
        '''
        # get a new header
        header_slt = HeadersSelector()
        header = header_slt.select_header()

        seed_url = self._address
        # execute every 10 mintues
        self.crawl(seed_url,callback=self.fetch_links, validate_cert=False, retries=10,headers=header,age=20*60, auto_recrawl=True,fetch_type="js")
        logger.info("################# on_start:" +seed_url)

    @config(age=-1,priority=2)
    def fetch_links(self, response, task):
        '''
            1. fetch the news url  from the response and callig into detail_page function
        '''
        # get a new header
        header_slt = HeadersSelector()
        header = header_slt.select_header()
        i = 0
        # step 1 :      fetch the news url  from the response and callig into detail_page function
        for query in ["#Con11 a","#Con21 a","#Con31 a","#Con41 a","#Con51 a","#Con61 a","#Con71 a","#Con81 a","#Con91 a"]:
            for e in response.doc.items(query):
                detail_url = e.attr['href']
                if detail_url:
                    # each detail_page task wile execute after 1 second, one by one
                    self.crawl(detail_url,callback=self.detail_page, validate_cert=False,exetime=time.time()+ i * 10,retries=3,headers=header)
                    i = i + 1
                    logger.info("################# next_page->detail_url:" + detail_url)

    @config(priority=1,age=-1)
    def detail_page(self, response, task):
        '''
            fetching url, title, content, date
        '''
        # date format : '2018年05月31日 15:12:17'
        date = datetime.today().strftime('%Y年%m月%d日 %H:%M:%S')

        title = response.doc('.main-title').text()

        source = response.doc('.source').text()

        content = ""
        for e in response.doc.items('.article  p'):
            content += e.text()

        # filter rules
        content = self.filter(content)

        # raw type transfer to result type
        raw = {
            "url": task['url'],
            "date": date,
            "title": title,
            "source":source,
            "content":content,
        }
        return self.raw2result(raw)

    def on_finished(self, response, task):
        '''called when all tasks finished'''
        logger.info("################# on_finished:"+task['url'])

    def filter(self,content):
        """
        remove the useless info of the content
        :param content: str
        :return: str
            the filtered content
        """
        # TODO: add specified filter rules
        return content

    def raw2result(self,raw):
        """
        transfer from raw to result
        :param raw: dict
        :return: dict
        """
        # url to docno
        assert raw["url"]
        raw["docno"] = str(hash(raw["url"]))

        # text rank
        textrank([raw])

        # sim hash
        raw["simhash"] = simhash(raw["textrank"])

        return raw
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
    _address = 'https://s.weibo.com/top/summary?cate=realtimehot'

    #   title
    _title = ""
    # url
    _url = ""

    def get_taskid(self, task):
        return task['url']

    @config(priority=3)
    def on_start(self):
        '''
        seeds .
        fetching 365 days news
        will calliing the next_page function
        '''
        # get a new header
        header_slt = HeadersSelector()
        header = header_slt.select_header()

        seed_url = self._address
        # execute every 10 mintues
        self.crawl(seed_url,callback=self.fetch_links, validate_cert=False, retries=10,headers=header,age=10*60, auto_recrawl=True,fetch_type="js")
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
        for e in response.doc.items('.td_02 a'):
            detail_url = e.attr['href']
            self._url = detail_url
            self._title = e.text()
            if detail_url:
                # each detail_page task wile execute after 1 second, one by one
                self.crawl(detail_url,callback=self.detail_page, validate_cert=False,exetime=time.time()+ i * 1,retries=3,headers=header,fetch_type="js")
                i = i + 1
                logger.info("################# next_page->detail_url:" + detail_url)

    @config(priority=1,age=-1)
    def detail_page(self, response, task):
        '''
            fetching url, title, content, date
        '''
        # date format : '2018年05月31日 15:12:17'
        date = datetime.today().strftime('%Y年%m月%d日 %H:%M:%S')
        content = ""
        for e in response.doc.items('.comment_txt'):
            content += e.text()

        # filter rules
        content = self.filter(content)

        # raw type transfer to result type
        raw = {
            "url": task['url'],
            "date": date,
            "title": self._title,
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
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-02-03 15:23:32
#
#target address:
#  http://news.ifeng.com/listpage/11502/20180321/1/rtlist.shtml
#

from pyspider.libs.base_handler import *
from datetime import timedelta, datetime
from log.logger import *
import time
from core.textrank import textrank
from core.simhash import simhash

logger = getLogger("news.ifeng.com")

class Handler(BaseHandler):
    crawl_config = {
    }

    '''
        address rule:
        http://news.ifeng.com/listpage/11502/date/page_no/rtlist.shtml
        example:
        http://news.ifeng.com/listpage/11502/20180321/1/rtlist.shtml
    '''
    _address_prefix = 'http://news.ifeng.com/listpage/11502'
    _page_no = 1
    _address_postfix = 'rtlist.shtml'
    # how long the day to be crawled
    _long = 30;
    '''
        taskid : the same with url
    '''
    def get_taskid(self, task):
        return task['url']

    @config(priority=0)
    def on_start(self):
        '''
        seeds .
        fetching 365 days news
        will calliing the next_page function
        '''
        for i in range(self._long):
            date = datetime.today() + timedelta(-i)
            date = date.strftime('%Y%m%d')
            seed_url = self._address_prefix + '/'+ date + '/' + str(self._page_no) + '/' +  self._address_postfix
            # each spider seed wile execute after 10 mintues, one by one
            self.crawl(seed_url,callback=self.next_page, validate_cert=False,exetime=time.time()+ i * 600, retries=3)
            logger.info("################# on_start:" +seed_url)

    @config(age=-1,priority=1)
    def next_page(self, response, task):
        ''' 1.fetch the news url  from the response and callig into detail_page function
            2.calling next_page function if its has next page
        '''
        # http://news.ifeng.com/listpage/11502/20180321/1/rtlist.shtml
        # news title
        detail_elements = response.doc.items('.left li > a')
        i = 0;
        # step 1 :      fetch the news url  from the response and callig into detail_page function
        for e in detail_elements:
            detail_url = e.attr['href']
            if detail_url:
                # each detail_page task wile execute after 0.5 second, one by one
                self.crawl(detail_url,callback=self.detail_page, validate_cert=False,exetime=time.time()+ i * 0.5,retries=3)
                i = i + 1
                logger.info("################# next_page->detail_url:" + detail_url)

        # step 2:    calling next_page function if its has next page
        i = 0;
        next_page_element = response.doc.items('span > a')
        for e in next_page_element:
            next_page_url = e.attr['href']
            if e.text().lstrip() == "下一页" and next_page_url:
                # each next_page task wile execute after 0.5 second, one by one
                self.crawl(next_page_url,callback=self.next_page, validate_cert=False,exetime=time.time()+ i * 50,retries=3)
                logger.info("################# next_page->next_page_url:")
                break

    @config(priority=2,age=-1)
    def detail_page(self, response, task):
        '''
            fetching url, title, contemt, date
        '''
        # fetching date from the url  http://news.ifeng.com/listpage/11502/20180321/1/rtlist.shtml
        dir_date = task['url'][24:32]
        content = ""
        for e in response.doc.items('div#main_content.js_selection_area p'):
            c = e.text()
            bre = False
            # delete <p> start with "原标题:" "资料|" "校对|"
            for s in ["原标题:","资料|","校对|"]:
                if c.startswith(s):
                    bre = True
                    break
            if bre:
                break
            content += e.text()

        # filter rules
        content = self.filter(content)

        # raw type transfer to result type
        raw = {
            "url": task['url'],
            "date": response.doc('[itemprop="datePublished"]').text().lstrip(),
            "title": response.doc('[itemprop="headline"]').text(),
            "content":content,
            "dir_date":dir_date,
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
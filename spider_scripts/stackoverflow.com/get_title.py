#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-02-03 15:23:32
# Project: Tenxun_News

from pyspider.libs.base_handler import *
import random
import string
import logging
from pyspider.database import connect_database

logger = logging.getLogger("sohu")


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(seconds=5)
    def on_start(self):
        print("on_start")
        self.crawl(
            "https://stackoverflow.com/questions/42587118/python-builtin-function-or-method-object-is-not-iterable-error",
            callback=self.index_page, validate_cert=False)

    @config(age=60 * 24)
    def index_page(self, response):
        print("index_page")
        self.crawl(
            "https://stackoverflow.com/questions/42587118/python-builtin-function-or-method-object-is-not-iterable-error",
            callback=self.detail_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        print("detail_page")
        return {
            "url": "baidu",
            "title": response.doc('title').text(),
        }

    # 配置taskid
    def get_taskid(self, task):
        print("get_taskid")
        s = task['url'] + '##'
        for _ in range(15):
            s += random.choice(string.ascii_letters + string.digits)
        return s

    # def on_result(self, task, result):
    #    print ("on_result")

    # 队列为0时触发的回调
    def on_finished(self, response, task):
        logger.info("on_finished################################################")
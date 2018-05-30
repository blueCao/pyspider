#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-03-22
#
#   saving spider result into mongodb
#

from pyspider.result import ResultWorker
from log.logger import *
import mongodb.mongo_cli as mongo

logger = getLogger("pyspider.mongodb_result_worker")
# mongo cli
cli = mongo.__get__()
# mongo database
database_name = "keepindoors"
# mongo collection
collection_name = "docs"

class MyResultWorker(ResultWorker):
    def on_result(self, task, result):
        # 抓取到的数据不为空
        assert task['taskid']
        assert task['project']
        assert task['url']
        assert result['url']
        assert result['title']
        assert result['content']
        assert result['date']
        assert result['docno']
        assert result['dir_date'],mongo
        assert result["content"]
        assert result["textrank"]
        assert result["simhash"]

        # save into mongodb if not duplicated
        if not mongo.getCollection(cli,database_name,collection_name).find_one("{docno:"+result["docno"]+"}"):
            mongo.insertDoc(result,cli,database_name,collection_name)
            logger.info("project=%s,taskid=%s,url=%s,result=%s",task['project'],task['taskid'],task['url'],result["title"])
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-03-22
#
#   saving spider result into files
#

from pyspider.result import ResultWorker
import logging
import os
import time

logger = logging.getLogger("result_worker")

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

        logger.info("project=%s,taskid=%s,url=%s,result=%s",task['project'],task['taskid'],task['url'],result)
        # 保存文件到指定的域名文件夹
        dir_path = self.fetch_dir_path(task)
        # 按照日期写入不同的文件
        date = time.strftime("%Y-%m-%d")
        if result['dir_date']:
            date = result['dir_date']
        fp = open(dir_path+'/'+date+'.result','a')
        # 将结果按照行分隔符|||写入文件中
        line_sep = '#####################################################################################\n'
        result.pop('dir_date')
        for key in result.keys():
            fp.write(result[key])
            fp.write('\n')
        fp.write(line_sep)
        fp.close()

    def fetch_dir_path(self,task):
        """
        根据不同的任务，生成对应的目录名，检查目录是否存在，不存在则新建一个
        """

        #  根据url获取对应的目录名
        #  规则如下：
        #       http://www.baidu.com/a/b/c                      目录   www.baidu.com/com/a/b/c
        #       http://www.baidu.com/a/b/c?param1=2&paraw=3     目录   www.baidu.com/com/a/b/c
        begin_index = task['url'].find("//")+2
        end_index = task['url'].find('/',begin_index)
        if end_index < 0:
            end_index == task['url']
        path = "./result/" + task['url'][begin_index:end_index]
        if os.path.exists(path) == False:
            os.makedirs(path)
            return path
        else:
            return path
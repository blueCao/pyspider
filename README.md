# [开源爬虫工具pyspider](https://github.com/binux/pyspider)的配置和使用
### 安装pyspider
```
pip install pyspider
```
### 启动pyspider
```
# 根据配置文件，一次性启动所有组件（scheduler,fetcher,processor,result_worker,webui）
pyspider -c config.json


# 分别启动每一个组件
# start **only one** scheduler instance
pyspider -c config.json scheduler

# phantomjs
pyspider -c config.json phantomjs

# start fetcher / processor / result_worker instances as many as your needs
pyspider -c config.json --phantomjs-proxy="localhost:25555" fetcher
pyspider -c config.json processor
pyspider -c config.json result_worker

# start webui, set `--scheduler-rpc` if scheduler is not running on the same host as webui
pyspider -c config.json webui
```

### 详细的安装使用方法参考
[中文文档](http://www.pyspider.cn/book/pyspider/pyspider-Quickstart-2.html)  
[英文文档](http://docs.pyspider.org/en/latest/Quickstart/)

### 使用举例
- 每隔5秒获爬取百度首页的标题信息，并把爬取的 url地址、标题信息 按照域名信息保存在本地文件中

### 目录信息
- data\
> 默认使用的所使用的SQLite数据库文件（pyspider指定projectdb、taskdb使用SQLite存储）

- result\
> 结果保存目录

- spider_scripts\
> 根据每个站点对应的爬虫脚本

- config.json
> pyspider启动指定的配置文件

- my_result_worker.py
> 自定义reslt_worker的结果处理方式,每次获得结果后自动触on_result方法，指定保存文件的操作。默认的on_result方法将结果保存在SQLite中，保存在文件中需要自己指定
对应的类，这个类正是起到这个作用

- requirements.txt
> pyspider需要用的所有包

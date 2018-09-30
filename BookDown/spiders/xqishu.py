# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import os
from ..items import File
import shelve
#item
"""
    URL = scrapy.Field()
    PATH = scrapy.Field()
"""

#爬虫
#关闭爬虫self.crawler.engine.close_spider(self, 'response msg error %s, job done!' % response.text)

class Spider(scrapy.Spider):
    name = 'xqishu'#爬虫名称
    start_urls = 'http://m.xqishu.com/'
    baseurl = 'http://m.xqishu.com' #host
    #访问首页
    def start_requests(self):
        self.lists = []
        print("爬取的小说类型：",self.settings['BOOK_CLASS'])
        print(f"爬取的小说大小[{self.settings['MINBOOKSIZE']} KB - {self.settings['MAXBOOKSIZE']} KB ]")
        #加载缓存
        self.path = self.settings["CACHE_LOG"]
        with shelve.open(self.path) as file:
            if "log" in file.keys():
                self.data = dict(file['log'])
                file.close()
            else:
                self.data = dict()
        print("读取缓存成功：",self.path)
        if 'index' in self.data.keys() and self.data['index'] == self.start_urls:
            pass #self.crawler.engine.close_spider(self, f"错误：此网站已经爬取过了，请清空缓存再爬取，LOG:{self.path},{self.data.keys()},{self.data}")
        print("请求首页")
        yield Request(self.start_urls,self.indexParse)

    #获取分析首页信息，并请求分类页面
    def indexParse(self,response):
        book_class = response.xpath("//div[@class='menu']/a")[1:-1] #获取分类页：最新、玄幻。。。。
        #访问记录
        key = response.url
        if key not in self.data.keys():
            self.data[key] = []

        #print(response.text)
        for bc in book_class:
            cl = bc.xpath("./text()").extract()[0]
            #不是要获取的类型忽略
            if cl not in  self.settings['BOOK_CLASS']:
                continue
            #看是否已经遍历
            url = self.baseurl + bc.xpath("./@href").extract()[0]
            if url not in self.data[key]:
                # 请求子页
                meta = {'class': cl, 'father': key}  # 发起请求，并记录分类
                yield Request(url, callback=self.pageParse, meta=meta)
            else:
                print(f"url：{url} 已访问")

            #表示首页已访问完毕
            self.data['index'] = key
    #获取电子书页面
    def pageParse(self,response):
        # 获取列表项
        lista = response.xpath("//ul[@class='book_list']/li")
        meta = response.meta
        # 访问记录
        key = response.url
        if key not in self.data.keys():
            self.data[key] = []
        father = meta ['father']
        meta['father'] = key
        #请求详情页
        for a in lista:
            url = self.baseurl+a.xpath(".//a/@href").extract()[0]
            if url not in self.data[key]:
                yield Request(url,callback=self.detailParse,meta=meta)
            else:
                print(f"url：{url} 已访问")
        #获取下一页
        next = response.xpath("//a[@id='pt_next']/@href").extract()
        if next:
            nexturl = self.baseurl+next[0]
            print("next url:",nexturl)
            if nexturl not in self.data[key]:
                yield Request(nexturl,callback=self.pageParse,meta=meta)
            else:
                print(f"url：{nexturl} 已访问")
        #此页已获取结束
        self.data[father].append(key)
    #获取详情页
    def detailParse(self,response):
        meta = response.meta
        # 访问记录
        key = response.url
        if key not in self.data.keys():
            self.data[key] = []
        father = meta['father']
        meta['father'] = key

        down = response.xpath("//a[@class='bdbtn greenBtn']/@href").extract()[0] #请求下载页
        url = self.baseurl+down
        if url not in self.data[key]:
            yield Request(url,callback=self.downParse,meta=meta)
        else:
            print(f"url：{url} 已访问")
        # 此页已获取结束
        self.data[father].append(key)
    #获取分析下载页
    def downParse(self,response):
        meta = response.meta
        # 访问记录
        key = response.url
        father = meta['father']
        try:
            cl = meta['class']
            if len(response.text) == 0:
                return

			#获取下载链接
            url = response.xpath("//a[@class='bdbtn greenBtn']/@href").extract()[0]
            #获取大小
            sizestr = response.xpath("//span[@class='num']/text()").extract()[0]
            size = float(sizestr[:-2])
            if 'MB' in sizestr or 'Mb' in sizestr or 'mB' in sizestr or 'mb' in sizestr:
                size = 1024*size
            #大小不符合不下载
            if size<float(self.settings['MINBOOKSIZE']) or size>float(self.settings['MAXBOOKSIZE']):
                print(f"丢弃item {url.split('/')[-1]}，原因：大小[{size} KB]太小")
                return
            print(f"获得 item {url.split('/')[-1]}，大小：[{sizestr}")
            #获取标题
            title = response.xpath("//h1[@class='title']/text()").extract()[0]
            txt = File()
            txt['PATH'] = cl +"/"+ sizestr+"_"+url.split('/')[-1] #生成文件名 小说类型/大小_小说名称
            txt['URL'] = [url]
            if os.path.exists(self.settings['FILES_STORE']+"/"+txt['PATH']) == True:
                print(f"丢弃item {url.split('/')[-1]}，原因：文件本地已存在")
                return
            #yield rar
            yield txt #下载
            # 此页已获取结束
            self.data[father].append(key)
        except Exception as e:
            print("发生错误：",e)
    def close(self, reason):
        with shelve.open(self.path) as file:
            file['log'] = self.data
            file.close()
        print("缓存成功：",self.path)
        super(Spider,self).close(self,reason)
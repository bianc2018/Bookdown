# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import os
from ..items import File
from scrapy.exceptions import CloseSpider
from ..Updata import Updata
"""
    URL = scrapy.Field()
    PATH = scrapy.Field()
"""

#爬虫
#关闭爬虫self.crawler.engine.close_spider(self, 'response msg error %s, job done!' % response.text)
#scrapy.log.msg(message, level=IN FO, spider=None)
class Spider(scrapy.Spider):
    name = 'aihu99'#爬虫名称
    start_urls = 'http://www.aihu99.com/'
    baseurl = 'http://www.aihu99.com/' #host
    #访问首页
    def start_requests(self):
        #print("更新。。。。。。。。")
        #self.up = Updata(self.settings['FILES_STORE'],self.settings['UPDATA_FILE'])
        print(f"爬取的小说类型：{self.settings['BOOK_CLASS']},空 即爬取全部")
        print(f"爬取的小说大小[{self.settings['MINBOOKSIZE']} KB - {self.settings['MAXBOOKSIZE']} KB ]")
        print(f"请求首页：{self.start_urls}")
        yield Request(self.start_urls,self.indexParse)

    #获取分析首页信息，并请求分类页面
    def indexParse(self,response):
        book_class = response.xpath("//div[@class='subnav']//a")[1:] #获取分类页：最新、玄幻。。。。
        #print(response.text)
        for bc in book_class:
            cl = bc.xpath("./@title").extract()[0]
            url = bc.xpath("./@href").extract()[0]

            if len(self.settings['BOOK_CLASS']) != 0:
                if cl not in self.settings['BOOK_CLASS']:
                    continue

            if cl == "最近更新":
                url = "http://www.aihu99.com/library/0_0_0_2_default_0_1.html"
                yield Request(url, callback=self.updataParse)
            else:
                yield Request(url, callback=self.pageParse)
    #更新
    def updataParse(self,response):
        print("更新。。。。。。。。")
        self.up = Updata(self.settings['FILES_STORE'], self.settings['UPDATA_FILE'])
        # 获取列表项
        lista = response.xpath("//li[@class='storelistbt5a']")
        # 请求详情页
        # 直接下载 http://down.aihu99.com/Txt_id/标题.txt
        for a in lista:
            try:
                id = a.xpath(".//a/@href").extract()[1].split("/")[-1].split(".")[0]
                classname = a.xpath(".//p/a/text()").extract()[2]
                title = a.xpath(".//a/@title").extract()[0]
                # 获取大小
                sizestr = a.xpath(".//p[3]").extract()[0].split("B")[0].split("：")[-1]
                size = float(sizestr[:-1])
                if 'M' in sizestr or 'm' in sizestr:
                    size = 1024 * size
                    # 大小不符合不下载
                if size < float(self.settings['MINBOOKSIZE']) or size > float(self.settings['MAXBOOKSIZE']):
                    print(f"丢弃item {title}，原因：大小[{size} KB]太小")
                else:
                    self.up.log(sizestr + "B_" + title + ".txt",classname)
                    classname = "最新全本"
                    txt = File()
                    txt['PATH'] = classname + "/" + sizestr + "B_" + title + ".txt"  # 生成文件名 小说类型/大小_小说名称
                    txt['URL'] = [f"http://down.aihu99.com/Txt_{id}/{title}.txt"]

                    if os.path.exists(self.settings['FILES_STORE'] + "/" + txt['PATH']) == True:
                        print(f"丢弃item {url.split('/')[-1]}，原因：文件本地已存在")
                    else:
                        yield txt;
            except Exception as e:
                print("发生错误：", e)

        # 发起请求
        i = 2
        end = response.xpath("//div[@class='yema']/a/@href")[-1].extract()
        while True:
            url = f"http://www.aihu99.com/library/0_0_0_2_default_0_{i}.html"
            yield Request(url, callback=self.Updatadown)
            if url == end:
                break;
            i+=1

    def Updatadown(self,response):
        # 获取列表项
        lista = response.xpath("//li[@class='storelistbt5a']")
        # 请求详情页
        # 直接下载 http://down.aihu99.com/Txt_id/标题.txt
        for a in lista:
            try:
                id = a.xpath(".//a/@href").extract()[1].split("/")[-1].split(".")[0]
                classname = a.xpath(".//p/a/text()").extract()[2]
                title = a.xpath(".//a/@title").extract()[0]
                # 获取大小
                sizestr = a.xpath(".//p[3]").extract()[0].split("B")[0].split("：")[-1]
                size = float(sizestr[:-1])
                if 'M' in sizestr or 'm' in sizestr:
                    size = 1024 * size
                    # 大小不符合不下载
                if size < float(self.settings['MINBOOKSIZE']) or size > float(self.settings['MAXBOOKSIZE']):
                    print(f"丢弃item {title}，原因：大小[{size} KB]太小")
                else:
                    self.up.log(sizestr + "B_" + title + ".txt", classname)
                    classname = "最新全本"
                    txt = File()
                    txt['PATH'] = classname + "/" + sizestr + "B_" + title + ".txt"  # 生成文件名 小说类型/大小_小说名称
                    txt['URL'] = [f"http://down.aihu99.com/Txt_{id}/{title}.txt"]

                    if os.path.exists(self.settings['FILES_STORE'] + "/" + txt['PATH']) == True:
                        print(f"丢弃item {title}，原因：文件本地已存在")
                    else:
                        yield txt;
            except Exception as e:
                print("发生错误：", e)
    #获取电子书页面
    def pageParse(self,response):
        # 获取列表项
        lista = response.xpath("//div[@class='listbg']")

        #请求详情页
        #直接下载 http://down.aihu99.com/Txt_id/标题.txt
        for a in lista:
            try:
                id = a.xpath(".//a/@href").extract()[0].split("/")[-1].split(".")[0]
                classname = a.xpath(".//span[@class='classname']/text()").extract()[0][1:-1]
                title = a.xpath(".//a/@title").extract()[0]
                #获取大小
                sizestr = a.xpath(".//span[@class='mainGreen']/text()").extract()[2].split("B")[0]
                size = float(sizestr[:-1])
                if 'M' in sizestr or 'm' in sizestr :
                    size = 1024 * size
                    # 大小不符合不下载
                if size < float(self.settings['MINBOOKSIZE']) or size > float(self.settings['MAXBOOKSIZE']):
                    print(f"丢弃item {title}，原因：大小[{size} KB]太小")
                else:
                    txt = File()
                    txt['PATH'] = classname + "/" + sizestr + "B_" + title+".txt"  # 生成文件名 小说类型/大小_小说名称
                    txt['URL'] = [f"http://down.aihu99.com/Txt_{id}/{title}.txt"]
                    if os.path.exists(self.settings['FILES_STORE'] + "/" + txt['PATH']) == True:
                        print(f"丢弃item {title}，原因：文件本地已存在")
                    else:
                        yield txt;
            except Exception as e:
                print("发生错误：",e)
        #获取下一页
        next = response.xpath("//a[@class='next']/@href").extract()
        if next:
            print("next url:",next[0])
            yield Request(next[0],callback=self.pageParse)
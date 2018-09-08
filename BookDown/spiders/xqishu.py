# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import os
from ..items import File
import shelve
import json

"""
    URL = scrapy.Field()
    PATH = scrapy.Field()
"""

LOG_PATH = './Books/log'
class Spider(scrapy.Spider):
    name = 'xqishu'
    start_urls = 'http://m.xqishu.com/'
    baseurl = 'http://m.xqishu.com'

    def start_requests(self):
        self.lists = []
        yield Request(self.start_urls,self.indexParse)

    def indexParse(self,response):
        book_class = response.xpath("//div[@class='menu']/a")[1:-1]
        #print(response.text)
        for bc in book_class:
            cl = bc.xpath("./text()").extract()[0]
            url = self.baseurl+bc.xpath("./@href").extract()[0]
            meta = {'class': cl}
            yield Request(url,callback=self.pageParse,meta=meta)

    def pageParse(self,response):
        lista = response.xpath("//ul[@class='book_list']/li")
        meta = response.meta

        for a in lista:
            url = self.baseurl+a.xpath(".//a/@href").extract()[0]
            yield Request(url,callback=self.detailParse,meta=meta)

        next = response.xpath("//a[@id='pt_next']/@href").extract()
        if next:
            nexturl = self.baseurl+next[0]
            print("next url:",nexturl)
            yield Request(nexturl,callback=self.pageParse,meta=meta)

    def detailParse(self,response):
        meta = response.meta
        down = response.xpath("//a[@class='bdbtn greenBtn']/@href").extract()[0]
        yield Request(self.baseurl+down,callback=self.downParse,meta=meta)

    def downParse(self,response):
        try:
            cl = response.meta['class']
            if len(response.text) == 0:
                return

            title = response.xpath("//h1[@class='title']/text()").extract()[0]
            
            #url = response.xpath("//a[@class='bdbtn downbtn']/@href").extract()[0]
            #rar= File()
            #rar['PATH'] = cl+'/'+title+'/'+url.split('/')[-1]
            #rar['URL'] = [url]

            url = response.xpath("//a[@class='bdbtn greenBtn']/@href").extract()[0]
            txt = File()
            txt['PATH'] = cl +"_"+ url.split('/')[-1]
            txt['URL'] = [url]

            about = response.xpath("//div[@class='con']/text()").extract()[0]

            self.lists.append([title])
            with shelve.open(LOG_PATH) as log:
                log['book'] = self.lists
                log.close()
            with open(LOG_PATH + '.txt', 'a+') as logt:
                logt.writelines(title+":"+about+'\n')

            #yield rar
            yield txt
        except Exception as e:
            print("发生错误：",e)
# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import os
from ..items import File
from scrapy.exceptions import CloseSpider
import shelve
class Updata:
    def __init__(self,Basepath,datapath,baseclass = '最新全本'):
        try:
            self.file = shelve.open(datapath, writeback = True)
            for filename, cl in self.file.items():
                s =Basepath+'/'+baseclass+'/'+filename
                d =Basepath+'/'+cl+'/'+filename
                os.popen(f"copy {s} {d}")
                os.popen(f"del {s}")
                del self.file[filename]
        except Exception as e:
            print("初始化错误：",e)
            self.file.close()
    def log(self,filename,cl):
        self.file[filename] = cl;
    def __del__(self):
        self.file.close();
#item
"""
    URL = scrapy.Field()
    PATH = scrapy.Field()
"""

#爬虫
#关闭爬虫self.crawler.engine.close_spider(self, 'response msg error %s, job done!' % response.text)
#scrapy.log.msg(message, level=IN FO, spider=None)
class Spider(scrapy.Spider):
    name = 'xqishu'#爬虫名称
    start_urls = 'http://m.xqishu.com/'
    baseurl = 'http://m.xqishu.com' #host
    #访问首页
    def start_requests(self):
        print("更新。。。。。。。。")
        self.up = Updata(self.settings['FILES_STORE'],self.settings['UPDATA_FILE'])
        print(f"爬取的小说类型：{self.settings['BOOK_CLASS']},空 即爬取全部")
        print(f"爬取的小说大小[{self.settings['MINBOOKSIZE']} KB - {self.settings['MAXBOOKSIZE']} KB ]")
        print("请求首页")
        yield Request(self.start_urls,self.indexParse)

    #获取分析首页信息，并请求分类页面
    def indexParse(self,response):
        book_class = response.xpath("//div[@class='menu']/a")[1:-1] #获取分类页：最新、玄幻。。。。
        #print(response.text)
        for bc in book_class:
            cl = bc.xpath("./text()").extract()[0]

            url = self.baseurl + bc.xpath("./@href").extract()[0]
            meta = {'class': cl}  # 发起请求，并记录分类
            yield Request(url, callback=self.pageParse,meta=meta)
    #获取电子书页面
    def pageParse(self,response):
        # 获取列表项
        lista = response.xpath("//ul[@class='book_list']/li")

        #请求详情页
        for a in lista:
            url = self.baseurl+a.xpath(".//a/@href").extract()[0]
            yield Request(url,callback=self.detailParse,meta = response.meta)
        #获取下一页
        next = response.xpath("//a[@id='pt_next']/@href").extract()
        if next:
            nexturl = self.baseurl+next[0]
            print("next url:",nexturl)
            yield Request(nexturl,callback=self.pageParse,meta=response.meta)
    #获取详情页
    def detailParse(self,response):
        down = response.xpath("//a[@class='bdbtn greenBtn']/@href").extract()[0] #请求下载页
        url = self.baseurl+down
        yield Request(url,callback=self.downParse,meta=response.meta)
    #获取分析下载页
    def downParse(self,response):
        try:
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
            #获取分类
            cl = response.xpath("//p[@class='gray']/text()").extract()[0].split(':')[1]
            if response.meta['class'] =='最新全本':
                self.up.log(sizestr+"_"+url.split('/')[-1] ,cl)
                cl = '最新全本'

            txt = File()
            txt['PATH'] = cl +"/"+ sizestr+"_"+url.split('/')[-1] #生成文件名 小说类型/大小_小说名称
            txt['URL'] = [url]
            if os.path.exists(self.settings['FILES_STORE']+"/"+txt['PATH']) == True:
                print(f"丢弃item {url.split('/')[-1]}，原因：文件本地已存在")
                if len(self.settings['BOOK_CLASS'])==1 and self.settings['BOOK_CLASS'][0]=="最新全本":
                    raise CloseSpider('重复抓取')
            #yield rar
            yield txt #下载
        except CloseSpider as cs:
            raise cs
        except Exception as e:
            print("发生错误：",e)

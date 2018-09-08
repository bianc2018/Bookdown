# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
class FileDown(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        #print("path"+request.meta['path'])
        return request.meta.get('path', '')

    def get_media_requests(self, item, info):
        url = item['URL'][0]
        meta = {'path': item['PATH']}
        print(meta)
        yield Request(url=url, meta=meta)
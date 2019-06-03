# -*- coding: utf-8 -*-
#  Author: Pavlo Leskovych
import json

import scrapy


class UrlsSpider(scrapy.Spider):
    _MAX_PAGES = 1787
    _current_page = 0

    name = 'urls'
    allowed_domains = ['e27.co/startups']
    api_url = 'https://e27.co/startups/load_startups_ajax?all&per_page={}'
    start_urls = [api_url.format(_current_page)]

    def start_requests(self):
        try:
            for i in range(int(self._MAX_PAGES)):
                self._current_page += 1
                yield scrapy.Request(url=self.api_url.format(self._current_page),
                                     callback=self.parse)
        except Exception:
            self.log('End reached...')

    def parse(self, response):
        data = json.loads(response.body.decode())['pagecontent']
        # self.log(data)
        selector = scrapy.Selector(text=data)

        for entry in selector.css('div.row'):
            yield {
                'link': entry.css('a::attr(href)').extract_first() or None,
            }

    # def parse_last_page(self, response):
    #     data = json.loads(response.body.decode())['pagecontent']
    #     selector = scrapy.Selector(text=data)
    #
    #     selected_str = selector.css('div.btn-group > a::attr(href)').extract()[4] or None
    #     return selected_str[-4:]

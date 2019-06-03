# -*- coding: utf-8 -*-
#  Author: Pavlo Leskovych
import csv
import random
import re

import scrapy


class DetailsSpider(scrapy.Spider):
    name = 'details'

    _STARTUPS_COUNT = 250
    # _STARTUPS_COUNT = 10
    _CSV_FILENAME = 'urls.csv'

    allowed_domains = ['e27.co']
    start_urls = ['http://e27.co/startups/']

    def parse(self, response):
        urls = self.get_urls_from_csv()

        for url in urls:
            url = url[0] + '?json'
            self.log(url)
            yield scrapy.Request(url=url, callback=self.parse_profile)

    def parse_profile(self, response):
        # data = json.loads(response.body.decode())
        # self.log(data)
        selector = scrapy.Selector(response, type='html')

        #  Preparing description list to write into .csv file.
        description = selector.xpath("//div[@class='portlet-body']/p[@class='profile-desc-text']/"
                                     "text()").extract()
        desc = ''
        for paragraph in description:
            desc += paragraph.strip()

        desc_short = selector.xpath("//div[@class='row']/div[@class='col-md-10']/div[@class='row']/"
                                                "div[@class='col-md-12']/div/text()").extract_first() or None

        # desc += ' pleskovych@gmail.com, r.davydjuk@rambler.ru mememe@mail.ru'
        # desc_short += ' pleskovych@gmail.com, r.davydjuk@rambler.ru mememe@mail.ru'

        phones = re.findall(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}',
                            desc + ' ' + desc_short) or None
        e_mails = re.findall(r'[\w\.-]+@[\w\.-]+', desc + ' ' + desc_short) or None

        # tags = selector.xpath('//div[@class="row"]/div[@class="col-md-10"]/div[@class="row"]/'
        #                       'div[@class=col-md-12]/div[3]/span/a/text()').extract() or None

        tags = selector.xpath('//div[@class="row"]/div[@class="col-md-10"]/div[@class="row"]/div['
                       '@class="col-md-12"]/div[3]/span/a/text()').extract()
        if tags:
            print('tags: ' + ', '.join(tags))

        items = {
            'company_name': selector.xpath("//h1[@class='profile-startup']/text()").extract_first() or None,
            'request_url': response.request.url[:-5] or None,
            'request_company_url': selector.css('div.mbt > span > a::attr(href)').extract_first() or None,
            'location': selector.css('div.col-md-10 > div.row > div.col-md-12 > div.mbt > span >'
                                     ' a::text').extract()[1] or None,
            'tags': tags,
            'founding_date': selector.xpath(
                "//div[@class='row']/div[@class='col-md-12']/p/span/text()").extract_first() or None,
            'founders': selector.xpath(
                "//div[@class='desc']/span[@class='item-label bold']/a/text()").extract() or None,
            # 'employee_range': selector.css('').extract_first() or None,
            'urls': selector.xpath("//div[@class='row']/div[@class='col-md-12']/div[@class='engage']/div[@class='row']"
                                   "/div[@class='col-md-5 socials pdt text-right ']/a/@href").extract() or None,
            'emails': e_mails or None,
            'phones': phones or None,
            'description_short': desc_short,
            'description': desc,
        }
        yield items

    def get_urls_from_csv(self):
        """
        In this method we get random 250 profile urls from .csv file
        that we created using e27_spider.py
        :return: list with 250 urls
        """
        urls_list = []

        with open(self._CSV_FILENAME) as file:
            urls_csv = list(csv.reader(file))
            length = len(urls_csv)
            for url in range(self._STARTUPS_COUNT):
                elem = urls_csv[random.randrange(length)]
                urls_list.append(elem)

        # self.log(urls_list)
        # self.log(len(urls_list))
        return urls_list

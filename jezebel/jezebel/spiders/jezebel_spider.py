import scrapy
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from jezebel.jezebel.items import Article
from bs4 import BeautifulSoup
import time

class JezebelSpider(scrapy.Spider):
    name = 'jezebel'
    allowed_domains = ['jezebel.com']
    start_urls = ['http://jezebel.com']
    handle_httpstatus_list = [404]

    def parse(self, response):

        for href in response.css('h1 a::attr(href)'):
            yield scrapy.Request(href.extract(), callback=self.parse_article)

        more_stories = response.css('div.load-more__button.dui > a').extract_first()
        if more_stories is not None:
            more_stories_link = '/' + BeautifulSoup(more_stories, 'lxml').find('a')['href']
            next_page = response.urljoin(more_stories_link)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        i = ItemLoader(item=Article(), response=response)
        i.add_xpath('title', '///header/header/h1/a')
        i.add_xpath('author', '///header/div/div[2]/div[1]/a')
        i.add_xpath('date', '///header/div/div[2]/time')

        s = BeautifulSoup(response.body, 'lxml')
        ptags = s.find_all('p')

        def get_text(p):
            return p.text

        text = ' '.join(map(get_text, ptags))
        i.add_value('text', text)
        i.add_value('url', response.url)

        return i.load_item()
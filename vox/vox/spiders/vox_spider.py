import scrapy
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from news_scrapers.vox.vox.items import Article
import datefinder
from bs4 import BeautifulSoup


class VoxSpider(scrapy.Spider):
    name = 'vox'
    allowed_domains = ['vox.com']
    start_urls = ['http://www.vox.com/news']

    handle_httpstatus_list = [404]

    def parse(self, response):
        for href in response.css('h3 a::attr(href)') + response.css('h2 a::attr(href)'):
            yield scrapy.Request(href.extract(), callback=self.parse_article)

        more_stories = response.css('#top > div.l-inner-wrap > div:nth-child(3) > div.m-pagination > div > span.m-pagination__next > a').extract_first()
        if more_stories is not None:
            more_stories_link = BeautifulSoup(more_stories, 'lxml').find('a')['href']
            next_page = response.urljoin(more_stories_link)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_article(self, response):
        i = ItemLoader(item=Article(), response=response)
        if response.css('body > div.off-canvas-wrap > div > section > div:nth-child(2) > div > div.article-lede.snippet.wide > h1') != []:
            i.add_css('title', 'body > div.off-canvas-wrap > div > section > div:nth-child(2) > div > div.article-lede.snippet.wide > h1')
        elif response.css('body > section > section > div:nth-child(2) > div > div.c-entry-hero__header-wrap > h1') == []:
            i.add_css('title', '# top > div > div.l-container > div > div.m-entry-feature__head-text > h1')
        else:
            i.add_css('title', 'body > section > section > div:nth-child(2) > div > div.c-entry-hero__header-wrap > h1')

        if response.css('body > div.off-canvas-wrap > div > section > div:nth-child(2) > div > div.article-lede.snippet.wide > p') != []:
            authordiv = response.css('body > div.off-canvas-wrap > div > section > div:nth-child(2) > div > div.article-lede.snippet.wide > p').extract_first()
            authorname = BeautifulSoup(authordiv).text
            i.add_value('author', authorname)
            i.add_value('date', 'NULL')
        elif response.css('body > section > section > div:nth-child(2) > div > div.c-byline > span:nth-child(1) > a') == []:
            authors = response.css('#top > div > div.l-container > div > div.m-entry-feature__head-text > p > a')
            names = [BeautifulSoup(n.extract()).text for n in authors]
            i.add_value('author', ', '.join(names))
            authordatediv = response.css('#top > div > div.l-container > div > div.m-entry-feature__head-text > p').extract_first()
            date = datefinder.find_dates(authordatediv)
            datestr = [str(d) for d in date]
            i.add_value('date', datestr[0])
        else:
            i.add_css('author', 'body > section > section > div:nth-child(2) > div > div.c-byline > span:nth-child(1) > a')
            i.add_css('date', 'body > section > section > div:nth-child(2) > div > div.c-byline > span:nth-child(2)')

        s = BeautifulSoup(response.body, 'lxml')
        ptags = s.find_all('p')

        def get_text(p):
            return p.text

        text = ' '.join(map(get_text, ptags))
        i.add_value('text', text)
        i.add_value('url', response.url)

        return i.load_item()


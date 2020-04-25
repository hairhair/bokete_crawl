import scrapy
from bs4 import BeautifulSoup

from bokete_crawl.items import Odai, Boke


"""
Todo
調査した結果, https://bokete.jp/odai/数字 (max. 5,076,872)
でお題が取ってこれる。これで100以上星がついてるbokeがあればcrawlするようにしたほうがいいかも
"""


class OdaiSpider(scrapy.Spider):
    name = 'odai'
    allowed_domains = ['bokete.jp/odai']
    start_urls = [
        f'https://bokete.jp/odai/{odai_id}' for odai_id in range(1, 5000000)
    ]

    def parse(self, response):
        if response.status != 200:
            return
        odai = self.parse_odai(response)
        odai['bokes'] = [boke for boke in self.parse_boke(response)]
        return odai

    def parse_odai(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        img_src = find_img_src(soup)
        return Odai(
            number=response.url.split('/')[-1],
            image_urls=[img_src]
        )

    def parse_boke(self, response):
        for boke in response.xpath('//div[@id="content"]/div[@class="boke"]'):
            text = boke.xpath('a[@class="boke-text"]/div/text()').get().strip()
            star_str = boke.xpath(
                    './/div[@class="boke-stars"]/a/text()'
                ).getall()[1].strip().replace(',', '')
            star = int(star_str)
            number = boke.xpath(
                    'a[@class="boke-text"]/@href'
                ).get().split('/')[-1]
            yield Boke(text=text, star=star, number=number)


def find_img_src(soup):
    img_src = 'https:' \
              + soup.find('div', attrs={'class': 'photo-content'}) \
                    .find('img').get('src')
    return img_src

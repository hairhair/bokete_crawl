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
        f'https://bokete.jp/odai/{odai_id}' for odai_id in range(1, 500000)
    ]

    def parse(self, response):
        if response.status != 200:
            return
        soup = BeautifulSoup(response.body, 'lxml')
        for odai in self.parse_odai(response):
            yield odai
            pass

    def parse_odai(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        img_src = find_img_src(soup)
        yield Odai(
            url=response.url,
            img_src=img_src,
            top_boke=find_top_boke(soup)
        )


def find_top_boke(soup):
    boke_elements = soup.find_all('div', attrs={'class': 'boke'})
    if len(boke_elements) < 2:
        return None     # 1つもボケのないお題
    top_boke = boke_elements[1]
    return Boke(
        star=find_boke_star(top_boke),
        text=find_boke_text(top_boke)
    )


def find_boke_star(soup) -> int:
    star_num = int(soup.find_all('div', attrs={'class': 'boke-stars'})[0]
                   .text.strip().replace(',', ''))
    return star_num


def find_boke_text(soup) -> str:
    return soup.find("a", attrs={"class": "boke-text"}).text.strip()


def find_img_src(soup):
    img_src = 'https:' \
              + soup.find('div', attrs={'class': 'photo-content'}) \
                    .find('img').get('src')
    return img_src


def find_max_boke_star(soup):
    # 評価順に元からsortされているので, 一番最初のbokeのみと比較するだけで良い
    boke_elements = soup.find_all('div', attrs={'class': 'boke'})
    if len(boke_elements) == 1:
        return None     # 1つもボケのないお題
    top_boke = boke_elements[1]
    return find_boke_star(top_boke)

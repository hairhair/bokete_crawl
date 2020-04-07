"""
Boketeのサイトをクローリングするスクリプト
"""
import requests
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
from time import sleep
import os
import pickle

PAGE_DIR = "https://bokete.jp"
ROOT_DIR = "https://bokete.jp/boke/legend"
PAGE_NUM = 1 # とりあえず

"""
Todo
調査した結果, https://bokete.jp/odai/{6桁の数字} (e.g. 009000)
でお題が取ってこれる。これで100以上星がついてるbokeがあればcrawlするようにしたほうがいいかも
"""


def save_image(boke):
    img_dir = "https:" + boke.find("img").get("src")
    img_binary = requests.get(img_dir)
    if img_binary.status_code is 200:
        image = Image.open(BytesIO(img_binary.content))
        filename = img_dir.split("/")[-1]
        image.save("../data/images/" + filename)
        return True
    else:
        return False

def crawl_one_boke(soup):
    # bokeのdivを抽出
    for boke in soup.find_all("div", attrs={"class": "boke"}):
        # 画像の保存
        is_saved = save_image(boke)
        # 対応するボケの保存
        meta_information = []
        caption_with_stars = []

        if is_saved:
            href = boke.find("a").get("href")
            odai_dir = PAGE_DIR + href
            req = requests.get(odai_dir)
            odai_soup = BeautifulSoup(req.text, "lxml")
            # 最初の<div class="boke">はお題
            for b_i, boke in enumerate(odai_soup.find_all("div", attrs={"class": "boke"})):
                if b_i == 0:
                    meta_infos = boke.find_all("a", attrs={"class": "btn btn-sm btn-default"})
                    # そのお題についたメタ情報の抽出
                    for meta_info in meta_infos:
                        meta_info.find("small").replace_with("")
                        tag_name = meta_info.text.strip()
                        meta_information.append(tag_name)
                else:
                    # bokeのテキスト部分のみ獲得
                    boke_text = boke.find_all("a", attrs={"class": "boke-text"})[0].text.strip()
                    star_num = boke.find_all("div", attrs={"class" : "boke-stars"})[0].text.strip()
                    caption_with_stars.append({
                        "star_num" : star_num,
                        "caption" : boke_text
                    })
    return {
        "meta_info" : meta_information,
        "captions" : caption_with_stars
    }

def crawl_bokete():
    captions = []
    for page_num in range(PAGE_NUM):
        if page_num == 0:
            req = requests.get(ROOT_DIR)
            soup = BeautifulSoup(req.text, "lxml")
            out = crawl_one_boke(soup)
        else:
            page_dir = os.path.join(ROOT_DIR, "?page=" + str(page_num+1))
            req = requests.get(page_dir)
            soup = BeautifulSoup(req.text, "lxml")
            out = crawl_one_boke(soup)
        captions.append(out)
        sleep(1)
    print("done")
    with open("../data/cations/crawled_captions.pkl", "wb") as f:
        pickle.dump(captions, f)

if __name__ == "__main__":
    crawl_bokete()
"""
Boketeのサイトをクローリングするスクリプト
"""
import os
import pickle
from io import BytesIO
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm

ROOT_DIR = "https://bokete.jp/odai"
ODAI_NUM = 500000   # 50万件

DATA_DIR = Path('../data')

"""
Todo
調査した結果, https://bokete.jp/odai/数字 (max. 5,076,872)
でお題が取ってこれる。これで100以上星がついてるbokeがあればcrawlするようにしたほうがいいかも
"""


def save_image(soup):
    img_dir = "https:" + soup.find_all("div", attrs={"class": "photo-content"})[0].find("img").get("src")
    img_binary = requests.get(img_dir)
    if img_binary.status_code is 200:
        image = Image.open(BytesIO(img_binary.content))
        filename = img_dir.split("/")[-1]
        image.save(DATA_DIR / f'images/{filename}')
        return True
    else:
        return False


def is_star_over_100(soup):
    # 評価順に元からsortされているので, 一番最初のbokeのみと比較するだけで良い
    try:
        top_boke = soup.find_all("div", attrs={"class": "boke"})[1]
    except IndexError:
        return False    # 1つもボケのないお題
    star_num = int(top_boke.find_all("div", attrs={"class": "boke-stars"})[0]
                   .text.strip().replace(',', ''))
    if star_num >= 100:
        return True
    else:
        return False


def crawl_one_boke(soup):
    # bokeのdivを抽出
    if is_star_over_100(soup):
        is_saved = save_image(soup)
        meta_information = []
        caption_with_stars = []
        if is_saved:
            for b_i, boke in enumerate(soup.find_all("div", attrs={"class": "boke"})):
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
            img_id = soup.find_all("div", attrs={"class" : "photo-content"})[0].find("img").get("src").replace("//", "").split("/")[-1]
            return {
                "meta_info" : meta_information,
                "captions" : caption_with_stars,
                "filename" : img_id
                }
        else:
            return None


def crawl_bokete():
    pbar = tqdm(range(1, ODAI_NUM + 1))
    for odai_num in pbar:
        pbar.set_description(f'boke/{odai_num}')
        odai_dump_path = DATA_DIR / f'captions/{odai_num}.pkl'
        if odai_dump_path.exists():
            continue    # 保存済みのお題をスキップ
        page_dir = os.path.join(ROOT_DIR, str(odai_num))
        req = requests.get(page_dir)
        if req.status_code is 200:
            soup = BeautifulSoup(req.text, "lxml")
            out = crawl_one_boke(soup)
            if out is not None:
                out["odai_num"] = odai_num
                with open(odai_dump_path, "wb") as f:
                    pickle.dump(out, f)
        sleep(1)


if __name__ == "__main__":
    crawl_bokete()
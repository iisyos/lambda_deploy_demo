import os
import requests
import re
import json
from bs4 import BeautifulSoup


class ImageCollector:
    query = ''
    dir = ''

    def __init__(self, query, dir='./data'):
        self.query = query
        self.dir = dir + '/' + query

    def get_soup(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"}
        params = {
            "q": self.query,  # search query
            "tbm": "isch",                # image results
            "hl": "ja",                   # language of the search
            "gl": "jp",                   # country where search comes from
            "ijn": "0"                    # page number
        }
        html = requests.get("https://www.google.com/search",
                            params=params, headers=headers, timeout=30)
        return BeautifulSoup(html.text, "lxml")

    def download_file(self, url, dst_path, index):
        response = requests.get(url)
        image = response.content

        with open(dst_path+'/' + str(index) + '.jpg', "wb") as path:
            path.write(image)

    def get_original_images(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        google_images = []

        all_script_tags = self.get_soup().select("script")

        matched_images_data = "".join(re.findall(
            r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

        matched_images_data_fix = json.dumps(matched_images_data)
        matched_images_data_json = json.loads(matched_images_data_fix)

        matched_google_image_data = re.findall(
            r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)

        matched_google_images_thumbnails = ", ".join(
            re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                       str(matched_google_image_data))).split(", ")

        thumbnails = [
            bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails
        ]

        removed_matched_google_images_thumbnails = re.sub(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', "", str(matched_google_image_data))

        matched_google_full_resolution_images = re.findall(
            r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", removed_matched_google_images_thumbnails)

        full_res_images = [
            bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape") for img in matched_google_full_resolution_images
        ]

        for index, (metadata, thumbnail, original) in enumerate(zip(self.get_soup().select('.isv-r.PNCib.MSM1fd.BUooTd'), thumbnails, full_res_images), start=1):
            google_images.append({
                "title": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["title"],
                "link": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["href"],
                "source": metadata.select_one(".fxgdke").text,
                "thumbnail": thumbnail,
                "original": original
            })

            print(f'Downloading {index} image...')
            self.download_file(thumbnail, self.dir, index)

        return google_images

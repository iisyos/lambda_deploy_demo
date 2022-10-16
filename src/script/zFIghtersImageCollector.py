from imageCollector import ImageCollector


class ZFIghtersImageCollector:
    Z_FIGHTER_NAMES = ['孫悟空', 'べジータ', '孫悟飯', '孫悟天', 'トランクス', 'ピッコロ', '天津飯', 'クリリン', 'ヤムチャ', '魔人ブウ', 'パイクーハン',
                       '人造人間18号', 'チャオズ', 'ヤジロベー', '亀仙人', '界王様', 'カリン様', 'ウーブ', 'ブロリー', 'バーダック', 'パラガス', 'ナッパ', 'ゴテンクス', 'ゴジータ', 'ベジット']

    def get_image(self):
        for name in self.Z_FIGHTER_NAMES:
            ImageCollector(name, './data').get_original_images()


if __name__ == '__main__':
    ZFIghtersImageCollector().get_image()

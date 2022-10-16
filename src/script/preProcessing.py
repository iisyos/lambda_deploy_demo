from PIL import Image
import glob
import os
import re


class PreProcessing:
    IMG_RELATIVE_DIR = '../data/train/**/*'
    DST_DIR = '../data/train/'

    def crop_center(self, pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                            (img_height - crop_height) // 2,
                            (img_width + crop_width) // 2,
                            (img_height + crop_height) // 2))

    def crop_max_square(self, pil_img):
        return self.crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def execute_crop_resize(self):
        files = glob.glob(self.IMG_RELATIVE_DIR)

        for f in files:
            try:
                img = self.crop_max_square(Image.open(f))
                img_resize = img.resize((112, 112))
                root, ext = os.path.splitext(f)
                base_name = os.path.basename(root)
                dir_name = re.sub(r'\d', "", base_name)
                img_resize.save(os.path.join(
                    self.DST_DIR + dir_name, base_name + ext))
            except OSError as e:
                pass

import os
import json

class Check_picture(object):
    def __init__(self, flie_path):
        self.flie_path = flie_path+'\\'
        self.img_names = []
        self.corrupt_num = 0

    def filter_picture(self):
        img_path = os.listdir(self.flie_path)
        choice = input('是否删除缺损图片[Y/N]:').lower()
        for img_name in img_path:
            # print(img_name)
            flie_suffix = os.path.splitext(img_name)[1].lower()
            if flie_suffix == '.jpg':
                with open(self.flie_path+img_name, 'rb') as flie:
                    flie.seek(-2, 2)
                    flie_data = flie.read()
                    if not flie_data.endswith(b'\xff\xd9'):
                        img_id = os.path.splitext(img_name)[0].lower().split('_')[6]
                        self.img_names.append(img_id)
                        self.corrupt_num += 1
                        self.delete_picture(choice, img_name)

            elif flie_suffix == '.png':
                with open(self.flie_path+img_name, 'rb') as flie:
                    flie.seek(-4, 2)
                    flie_data = flie.read()
                    if not flie_data.endswith(b'\xaeB`\x82'):
                        img_id = os.path.splitext(img_name)[0].lower().split('_')[6]
                        self.img_names.append(img_id)
                        self.corrupt_num += 1
                        self.delete_picture(choice, img_name)
        print('缺损图片 : %d张' % self.corrupt_num)
        print(self.img_names)

    def delete_picture(self, choice, img_name):
        if choice == 'y':
            os.remove(self.flie_path + img_name)

    def storage_id(self):
        with open('id.json', 'w') as data:
            data.write(json.dumps(self.img_names))

flie_path = 'D:\PycharmProjects\开课吧-Python爬虫\自主升级\Pixiv爬虫\img'
# flie_path = 'D:\PycharmProjects\开课吧-Python爬虫\自主升级\Pixiv作品下载\image'
check_picture = Check_picture(flie_path)
check_picture.filter_picture()
# check_picture.storage_id()

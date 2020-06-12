import gevent
from gevent import monkey
from gevent.queue import Queue
monkey.patch_all()
import requests

class Painting_download():
    def __init__(self):
        self.session = requests.session()
        self.work_1 = Queue()
        self.list_photo = []
        self.tasks_list_1 = []
        self.work_2 = Queue()
        self.tasks_list_2 = []

    def painting_id(self, ides):
        ides.replace('，', ',')
        id_list = ides.split(',')
        for id in id_list:
            self.work_1.put_nowait(id)

    def painting_XHR(self):
        while not self.work_1.empty():
            id_photo = self.work_1.get_nowait()
            url_works = 'https://www.pixiv.net/ajax/illust/{}/pages?lang=zh'.format(id_photo)
            headers_works = {
                'referer': 'https://www.pixiv.net/artworks/{}'.format(id_photo),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            res_works = self.session.get(url_works, headers=headers_works)
            print(res_works.status_code)
            json_works = res_works.json()
            for body_works in json_works['body']:
                url_original = body_works['urls']['original']
                self.list_photo.append([url_original, id_photo])

    def run_painting(self):
        for reptile in range(10):
            task_1 = gevent.spawn(self.painting_XHR)
            self.tasks_list_1.append(task_1)
        gevent.joinall(self.tasks_list_1)

    def urls(self):
        for urls_photo in self.list_photo:
            self.work_2.put_nowait(urls_photo)
        self.work_2_nums = self.work_2.qsize()
        return self.work_2_nums

    def download(self, path):
        while not self.work_2.empty():
            urls_photo = self.work_2.get_nowait()
            headers_photo = {
                'referer': 'https://www.pixiv.net/artworks/{}'.format(urls_photo[1]),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            res_photo = self.session.get(urls_photo[0], headers=headers_photo)
            print(res_photo.status_code)
            with open('{0}/{1}'.format(path, urls_photo[0].replace('https://i.pximg.net/img-original/img/', '').replace('/', '_')),'wb') as photo:
                photo.write(res_photo.content)
            work_2_num = self.work_2_nums - 1
            return (work_2_num, 'ID：{}……下载成功'.format(urls_photo[1]))

    def run_download(self, path):
        self.run_painting()
        self.urls()
        for reptile in range(5):
            task_2 = gevent.spawn(self.download, path)
            self.tasks_list_2.append(task_2)
        gevent.joinall(self.tasks_list_2)

if __name__ == '__main__':
    download = Painting_download()
    download.painting_id('82212425')
    download.run_download('image')

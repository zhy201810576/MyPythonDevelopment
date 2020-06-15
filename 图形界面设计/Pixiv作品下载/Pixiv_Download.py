from gevent import monkey; monkey.patch_all(thread=False)
from threading import Thread
import gevent
from gevent.queue import Queue
import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from requests.cookies import RequestsCookieJar
from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog, QTextBrowser
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Signal, QObject

class MySignals(QObject):
    text_print = Signal(QTextBrowser, str)
    progress_update = Signal(int)

class Pixiv():

    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        #可批量下载，如:111111,222222(逗号用英文)
        self.ui.lineEdit_illustID.setPlaceholderText('可批量下载，如:111111,222222(逗号用英文)')
        # self.ui.pushButton.clicked.connect(self.get_paint)
        # self.ui.pushButton_2.clicked.connect(self.get_path)
        MS.progress_update.connect(self.setProgress)
        MS.text_print.connect(self.printPace)

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.lineEdit_2.setText(path)

    def setProgress(self, value):
        self.ui.progressBar.setValue(value)

    def printPace(self, element, text):
        element.append(str(text))
        element.ensureCursorVisible()

    def get_paint(self):
        def State():
            state = True
            if self.ui.lineEdit.text() == '' or self.ui.lineEdit_2.text() == '':
                QMessageBox.warning(self.ui, '警告', 'ID与路径不能为空！！！')
                state = False
            return state

        def paint_thread():
            self.ui.textBrowser.setPlainText('======开始爬取======')
            PD.painting_id(self.ui.lineEdit.text())
            PD.Downloading(self.ui.lineEdit_2.text())
        # if State():
        #     paint_thread()
        try:
            if State():
                paint_thread()
        except:
            QMessageBox.critical(self.ui, '错误', '爬取失败，连接超时！！！')


class Pixiv_Login(Pixiv):
    def __init__(self):
        super(Pixiv_Login, self).__init__()
        self.session = requests.session()
        try:
            self.Get_login_info()
            self.Get_login_cookies()
        except FileNotFoundError:
            QMessageBox.warning(PP.ui, '警告', '请重新登录！！！')

    def Get_login_cookies(self):
        self.jar = RequestsCookieJar()
        with open('cookie.json', 'r') as cookie_txt:
            cookies_list = json.loads(cookie_txt.read())
            for cookie in cookies_list:
                self.jar.set(cookie['name'], cookie['value'])

    def Get_login_info(self):
        with open('info.json', 'r') as info:
            self.info_dict = json.loads(info.read())

class Illust_download(Pixiv_Login):
    def __init__(self):
        super(Illust_download, self).__init__()
        self.work_1 = Queue()
        self.list_photo = []
        self.tasks_list_1 = []
        self.work_2 = Queue()
        self.tasks_list_2 = []
        self.work_2_num = 0

    def painting_id(self, ides):
        ides = ides.replace('，', ',')
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
        PP.ui.progressBar.setRange(0, self.work_2_nums)

    def download(self, path):
        while not self.work_2.empty():
            urls_photo = self.work_2.get_nowait()
            headers_photo = {
                'referer': 'https://www.pixiv.net/artworks/{}'.format(urls_photo[1]),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            res_photo = self.session.get(urls_photo[0], headers=headers_photo)
            print(res_photo.status_code)
            with open('{0}/{1}'.format(path,
                                       urls_photo[0].replace('https://i.pximg.net/img-original/img/', '').replace('/',
                                                                                                                  '_')),
                      'wb') as photo:
                photo.write(res_photo.content)
            self.work_2_num = self.work_2_num + 1
            MS.text_print.emit(PP.ui.textBrowser, '第{}幅作品……下载成功'.format(self.work_2_num))
            MS.progress_update.emit(self.work_2_num)

    def run_download(self, path):
        for reptile in range(5):
            task_2 = gevent.spawn(self.download, path)
            self.tasks_list_2.append(task_2)
        gevent.joinall(self.tasks_list_2)

    def Downloading(self, path):
        def thread_download(path):
            self.run_painting()
            self.urls()
            self.run_download(path)

        thread = Thread(target=thread_download, args=(path,))
        # thread.setDaemon(True)
        thread.start()

MS = MySignals()
PD = Illust_download()
app = QApplication([])
PP = Pixiv()
PP.ui.show()
app.exec_()

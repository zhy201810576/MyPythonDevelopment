from gevent import monkey; monkey.patch_all(thread=False)
from threading import Thread
import gevent
from gevent.queue import Queue
import requests
from bs4 import BeautifulSoup
import os
import json
import base64
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
        self.ui.pushButton_Login.clicked.connect(self.Login)
        self.ui.pushButton_path.clicked.connect(self.get_path)
        self.ui.pushButton_illustID.clicked.connect(self.get_illust)
        self.ui.pushButton_authorID.clicked.connect(self.get_authorIllust)
        self.ui.pushButton_collect.clicked.connect(self.get_collectIllust)
        self.ui.pushButton_censorPicture.clicked.connect(self.censorPicture)
        MS.progress_update.connect(self.setProgress)
        MS.text_print.connect(self.printPace)

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.lineEdit_path.setText(path)

    def setProgress(self, value):
        self.ui.progressBar.setValue(value)

    def printPace(self, element, text):
        element.append(str(text))
        element.ensureCursorVisible()

    def Login(self):
        PL.Login_thread(self.ui.lineEdit_userID.text(), self.ui.lineEdit_password.text())

    def censorPicture(self):
        if self.ui.lineEdit_path.text() == '':
            QMessageBox.warning(self.ui, '警告', '路径不能为空！！！')
        elif self.ui.lineEdit_path.text() != '':
            PC = Check_picture(self.ui.lineEdit_path.text())
            PC.thread_FilterPic()

    def get_illust(self):
        def State():
            state = True
            if self.ui.lineEdit_illustID.text() == '' or self.ui.lineEdit_path.text() == '':
                QMessageBox.warning(self.ui, '警告', 'ID与路径不能为空！！！')
                state = False
            return state

        def illust():
            self.ui.textBrowser.setPlainText('======开始爬取======')
            PD.illustID(self.ui.lineEdit_illustID.text())
            PD.illust_download(self.ui.lineEdit_path.text())
        # if State():
        #     illust_thread()
        try:
            if State():
                illust()
        except:
            QMessageBox.critical(self.ui, '错误', '爬取失败，连接超时！！！')

    def get_authorIllust(self):
        def State():
            state = True
            if self.ui.lineEdit_authorID.text() == '' or self.ui.lineEdit_path.text() == '':
                QMessageBox.warning(self.ui, '警告', 'ID与路径不能为空！！！')
                state = False
            return state

        def illust_thread():
            self.ui.textBrowser.setPlainText('======开始爬取======')
            PD.Author_iIllust(self.ui.lineEdit_authorID.text(), self.ui.lineEdit_path.text())
        # if State():
        #     illust_thread()
        try:
            if State():
                illust_thread()
        except:
            QMessageBox.critical(self.ui, '错误', '爬取失败，连接超时！！！')

    def get_collectIllust(self):
        def State():
            state = True
            if self.ui.spinBox_page.value() == 0 or self.ui.lineEdit_path.text() == '':
                QMessageBox.warning(self.ui, '警告', '目标页数不能为0且路径不能为空！！！')
                state = False
            return state

        def collectIllust():
            self.ui.textBrowser.setPlainText('======开始爬取======')
            PD.Collect_page(self.ui.spinBox_page.value())
            PD.Collect_iIllust(self.ui.lineEdit_path.text())
        try:
            if State():
                collectIllust()
        except:
            QMessageBox.critical(self.ui, '错误', '爬取失败，连接超时！！！')

class Check_picture():
    def __init__(self, path):
        PP.ui.textBrowser.setPlainText('正在检测图片是否有缺损……')
        # MS.text_print.emit(PP.ui.textBrowser, '正在检测图片是否有缺损……')
        self.path = path
        self.flie_path = path+'\\'
        self.img_names = []
        self.corrupt_num = 0

    def filter_picture(self):
        img_path = os.listdir(self.flie_path)
        for img_name in img_path:
            # print(img_name)
            flie_suffix = os.path.splitext(img_name)[1].lower()
            if flie_suffix == '.jpg':
                flie = open(self.flie_path+img_name, 'rb')
                flie.seek(-2, 2)
                flie_data = flie.read()
                flie.close()
                if not flie_data.endswith(b'\xff\xd9'):
                    img_id = os.path.splitext(img_name)[0].lower().split('_')[6]
                    self.img_names.append(img_id)
                    self.corrupt_num += 1
                    self.delete_picture(img_name)

            elif flie_suffix == '.png':
                flie = open(self.flie_path+img_name, 'rb')
                flie.seek(-4, 2)
                flie_data = flie.read()
                flie.close()
                if not flie_data.endswith(b'\xaeB`\x82'):
                    img_id = os.path.splitext(img_name)[0].lower().split('_')[6]
                    self.img_names.append(img_id)
                    self.corrupt_num += 1
                    self.delete_picture(img_name)
        # print('缺损图片 : %d张' % self.corrupt_num)
        MS.text_print.emit(PP.ui.textBrowser, '缺损图片 : %d张' % self.corrupt_num)
        # print(self.img_names)
        if self.corrupt_num != 0:
            MS.text_print.emit(PP.ui.textBrowser, '======重新开始爬取======')
            PD.illustID(self.img_names)
            PD.illust_download(self.path)

    def delete_picture(self, img_name):
        os.remove(self.flie_path + img_name)

    def thread_FilterPic(self):
        thread_filterPic = Thread(target=self.filter_picture)
        thread_filterPic.setDaemon(True)
        thread_filterPic.start()

    def storage_id(self):
        with open('id.json', 'w') as data:
            data.write(json.dumps(self.img_names))

class Pixiv_Login():
    def __init__(self):
        self.session = requests.session()
        info_dict = self.Get_login_info()
        PP.ui.label_userName.setText(info_dict['userName'])
        PP.ui.lineEdit_userID.setText(info_dict['userID'])
        PP.ui.lineEdit_password.setText(base64.b64decode(info_dict['password'].encode('utf-8')).decode('utf-8'))
        self.session.cookies = self.Get_login_cookies()

    def Get_login_cookies(self):
        jar = RequestsCookieJar()
        with open('cookie.json', 'r') as cookie_txt:
            cookies_list = json.loads(cookie_txt.read())
            for cookie in cookies_list:
                jar.set(cookie['name'], cookie['value'])
        return jar

    def Get_login_info(self):
        with open('info.json', 'r') as info:
            info_dict = json.loads(info.read())
        return info_dict

    def Censor_cookies(self):
        url = 'https://www.pixiv.net/setting_user.php'
        login_code = self.session.get(url, allow_redirects=False)
        # print(login_code.status_code)
        if login_code.status_code != 200:
            MS.text_print.emit(PP.ui.textBrowser, '警告!……cookie已过期，请重新登录!！！')

    # def Censor_login(self):
    #     cookies = self.Get_login_cookies()
    #     url = 'https://www.pixiv.net/setting_user.php'
    #     login_code = requests.get(url, cookies=cookies, allow_redirects=False)
    #     # print(login_code.status_code)
    #     if login_code.status_code != 200:
    #         MS.text_print.emit(PP.ui.textBrowser, '……登录失败!!!')

    def Put_login_cookies(self, userID, password):
        MS.text_print.emit(PP.ui.textBrowser, '登录中loading……')
        option = webdriver.ChromeOptions()
        option.add_argument('headless')  # 静默模式
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(desired_capabilities=capa, chrome_options=option)
        driver.get(
            'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page')
        # time.sleep(5)
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="LoginComponent"]')))
        driver.execute_script("window.stop();")
        driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[1]/input').send_keys(userID)
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[2]/input').send_keys(password)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/button').click()
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.ID, 'qualaroo_dnt_frame')))
        # time.sleep(60)
        cookies_list = driver.get_cookies()
        # print(cookies_list)
        cookies_json = json.dumps(cookies_list)
        with open('cookie.json', 'w') as flie:
            flie.write(cookies_json)
        driver.close()
        info_dict = {}
        cookies = self.Get_login_cookies()
        url = 'https://www.pixiv.net/setting_user.php'
        login_code = requests.get(url, cookies=cookies, allow_redirects=False)
        # print(login_code.status_code)
        if login_code.status_code == 200:
            html_login = login_code.text
            soup_login = BeautifulSoup(html_login, 'html.parser')
            json_content = soup_login.find(id='meta-global-data')['content']
            userName = json.loads(json_content)['userData']['name']
            info_dict['userName'] = userName
            info_dict['userID'] = userID
            info_dict['password'] = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            with open('info.json', 'w') as info:
                info.write(json.dumps(info_dict))
            MS.text_print.emit(PP.ui.textBrowser, '……登录成功!')

    def Login_thread(self, userID, password):
        def Lodin_work(userID, password):
            self.Put_login_cookies(userID, password)
        thread_Login = Thread(target=Lodin_work, args=(userID, password, ))
        thread_Login.start()

class Illust_download(Pixiv_Login):
    # def __init__(self):
    #     super(Illust_download, self).__init__()
    #     self.work_1 = Queue()
    #     self.list_photo = []
    #     self.tasks_list_1 = []
    #     self.work_2 = Queue()
    #     self.tasks_list_2 = []
    #     self.work_2_num = 0

    def illustID(self, ides):
        id_list = []
        self.work_1 = Queue()
        if type(ides) == str:
            ides = ides.replace('，', ',')
            id_list = ides.split(',')
        elif type(ides) == list:
            id_list = ides
        for id in id_list:
            # print(id)
            self.work_1.put_nowait(id)

    def illust_info(self):
        self.list_photo = []
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

    def get_illust(self):
        self.tasks_list_1 = []
        for reptile in range(10):
            task_1 = gevent.spawn(self.illust_info)
            self.tasks_list_1.append(task_1)
        gevent.joinall(self.tasks_list_1)

    def urls(self):
        self.work_2 = Queue()
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
            MS.text_print.emit(PP.ui.textBrowser, '第{}张插画……下载成功'.format(self.work_2_num))
            MS.progress_update.emit(self.work_2_num)

    def run_download(self, path):
        self.tasks_list_2 = []
        self.work_2_num = 0
        MS.progress_update.emit(self.work_2_num)
        for reptile in range(5):
            task_2 = gevent.spawn(self.download, path)
            self.tasks_list_2.append(task_2)
        gevent.joinall(self.tasks_list_2)

    def illust_download(self, path):
        def thread_illust_download(path):
            self.__init__()
            self.Censor_cookies()
            self.get_illust()
            self.urls()
            self.run_download(path)
        thread = Thread(target=thread_illust_download, args=(path,))
        # thread.setDaemon(True)
        thread.start()

    def author_illust(self, authorID):
        illust_list = []
        id_author = authorID
        url_authorHome = 'https://www.pixiv.net/users/{}'.format(id_author)
        ulr_author = 'https://www.pixiv.net/ajax/user/{}/profile/all?lang=zh'.format(id_author)
        # headers_authorHome = {
        #     'referer': 'https://www.pixiv.net/users/{}/following'.format(id_author),
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        # }
        headers_author = {
            'referer': 'https://www.pixiv.net/users/{}'.format(id_author),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        res_authorHome = self.session.get(url_authorHome, headers=headers_author)
        res_author = self.session.get(ulr_author, headers=headers_author)
        print(res_authorHome.status_code, res_author.status_code)
        json_author = res_author.json()
        illusts = json_author['body']['illusts']
        soup_authorHome = BeautifulSoup(res_authorHome.text, 'html.parser')
        json_content = soup_authorHome.find(id='meta-preload-data')['content']
        self.userName = json.loads(json_content)['user'][id_author]['name']
        illust_num = len(illusts)
        MS.text_print.emit(PP.ui.textBrowser, '画师{0}共有{1}幅作品'.format(self.userName, illust_num))
        # print('画师{0}共有{1}幅作品'.format(userName, illust_num))
        for illust in illusts:
            illust_list.append(illust)
        PD.illustID(illust_list)


    def Author_iIllust(self, authorID, path):
        def work_Author_iIllust(authorID, path):
            self.__init__()
            self.Censor_cookies()
            self.author_illust(authorID)
            self.get_illust()
            self.urls()
            path = path + '\\' + self.userName
            os.mkdir(path)
            self.run_download(path)
        thread_Author_iIllust = Thread(target=work_Author_iIllust, args=(authorID, path,))
        # thread_Author_iIllust.setDaemon(True)
        thread_Author_iIllust.start()

    def Collect_page(self, page_num):
        self.work_3 = Queue()
        self.list_id_photo = []
        page = page_num
        for i in range(1, page + 1):
            self.work_3.put_nowait(str(i))

    def Collection(self):
        while not self.work_3.empty():
            page = self.work_3.get_nowait()
            url_collection = "https://www.pixiv.net/bookmark.php?rest=show&p={}".format(page)
            headers = {
                'referer': 'https://accounts.pixiv.net/login',
                'origin': 'https://accounts.pixiv.net',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            res_collection = self.session.get(url_collection, headers=headers)
            print(res_collection.status_code)
            html_collection = res_collection.text
            soup_collection = BeautifulSoup(html_collection, 'html.parser')
            list_collection = soup_collection.find_all(class_='image-item')
            # print(list_collection)
            for collection in list_collection:
                id_collection = collection.find(class_='ui-scroll-view')
                id_photo = id_collection['data-id']
                self.list_id_photo.append(id_photo)

    def Collect_iIllust(self, path):
        def work_Collect_iIllust(path):
            self.__init__()
            self.Censor_cookies()
            self.Collection()
            self.illustID(self.list_id_photo)
            self.get_illust()
            self.urls()
            self.run_download(path)
        thread_Collect_iIllust = Thread(target=work_Collect_iIllust, args=(path,))
        thread_Collect_iIllust.start()

app = QApplication([])
MS = MySignals()
PP = Pixiv()
PL = Pixiv_Login()
PD = Illust_download()
PP.ui.show()
app.exec_()

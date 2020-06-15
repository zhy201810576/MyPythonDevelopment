import gevent
from gevent import monkey
from gevent.queue import Queue

monkey.patch_all()

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


# headers = {
# 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
# 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
# }
#
# url_pixiv = 'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page'
# params_pixiv = {
# 'return_to': 'https://www.pixiv.net/',
# 'lang': 'zh',
# 'source': 'pc',
# 'view_type': 'page',
# }
# res_pixiv = session.get(url_pixiv, params=params_pixiv, headers=headers)
# print(res_pixiv.status_code)
# html_pixiv = res_pixiv.text
# soup_pixiv = BeautifulSoup(html_pixiv, 'html.parser')
# dicts_content = soup_pixiv.find(id='init-config')
# dict_content = json.loads(dicts_content['value'])
# post_key = dict_content['pixivAccount.postKey']
# print(post_key, type(post_key))
# url_login = 'https://accounts.pixiv.net/api/login?lang=zh'
# headers_pixiv = {
# 'Referer':'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=70639869',
# 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
# 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
# }
# data_login = {
# 'captcha': '',
# 'g_recaptcha_response': '',
# 'password': 'zhy08112',
# 'pixiv_id': '924868349@qq.com',
# 'post_key': '',
# 'source': 'pc',
# 'ref': '',
# 'return_to': 'https://www.pixiv.net/'
# }
#
# data_login['post_key'] = post_key
# login_in = session.post(url_login, headers=headers_pixiv, data=data_login)
# print(login_in.status_code)

# url = 'https://www.pixiv.net/setting_user.php'
# login_code = session.get(url, allow_redirects=False)
# print(login_code.status_code)

def Put_login_cookies():
    option = webdriver.ChromeOptions()
    option.add_argument('headless') # 静默模式
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(desired_capabilities=capa, chrome_options=option)
    driver.get(
        'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page')
    # time.sleep(5)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="LoginComponent"]')))
    driver.execute_script("window.stop();")
    driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[1]/input').send_keys("924868349@qq.com")
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[2]/input').send_keys("zhy08112")
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="LoginComponent"]/form/button').click()
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.ID, 'qualaroo_dnt_frame')))
    # time.sleep(60)
    cookies_list = driver.get_cookies()
    # print(cookies_list)
    cookies_json = json.dumps(cookies_list)
    with open('cookie.json', 'w') as flie:
        flie.write(cookies_json)
    driver.close()

def Get_login_cookies():
    jar = RequestsCookieJar()
    with open('cookie.json', 'r') as cookie_txt:
        cookies_list = json.loads(cookie_txt.read())
        for cookie in cookies_list:
            jar.set(cookie['name'], cookie['value'])
    return jar

session = requests.session()
try:
    session.cookies = Get_login_cookies()
except FileNotFoundError:
    Put_login_cookies()
    session.cookies = Get_login_cookies()

url = 'https://www.pixiv.net/setting_user.php'
login_code = session.get(url, allow_redirects=False)
print(login_code.status_code)
if login_code.status_code != 200:
    print('cookie已过期，请重新登录!')
    Put_login_cookies()
    session.cookies = Get_login_cookies()

list_id_photo = []
list_photo = []

work_1 = Queue()
page = int(input('请输入页数:'))
for i in range(1, page+1):
    work_1.put_nowait(str(i))

def Collection():
    while not work_1.empty():
        page = work_1.get_nowait()
        url_collection = "https://www.pixiv.net/bookmark.php?rest=show&p={}".format(page)
        headers = {
            'referer': 'https://accounts.pixiv.net/login',
            'origin': 'https://accounts.pixiv.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        res_collection = session.get(url_collection, headers=headers)
        print(res_collection.status_code)
        html_collection = res_collection.text
        soup_collection = BeautifulSoup(html_collection, 'html.parser')
        list_collection = soup_collection.find_all(class_='image-item')
        # print(list_collection)
        for collection in list_collection:
            id_collection = collection.find(class_='ui-scroll-view')
            id_photo = id_collection['data-id']
            list_id_photo.append(id_photo)
            # title_collection = collection.find(class_='title')
            # title_photo = title_collection['title']

tasks_list_1 = []
for reptile in range(5):
    task_1 = gevent.spawn(Collection)
    tasks_list_1.append(task_1)
gevent.joinall(tasks_list_1)
print(list_id_photo)

work_2 = Queue()
for id_photo in list_id_photo:
    work_2.put_nowait(id_photo)

def Works():
    while not work_2.empty():
        id_photo = work_2.get_nowait()
        url_works = 'https://www.pixiv.net/ajax/illust/{}/pages?lang=zh'.format(id_photo)
        headers_works = {
            'referer': 'https://www.pixiv.net/artworks/{}'.format(id_photo),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        res_works = session.get(url_works, headers=headers_works)
        # print(res_works.status_code)
        json_works = res_works.json()
        for body_works in json_works['body']:
            url_original = body_works['urls']['original']
            list_photo.append([url_original, id_photo])

tasks_list_2 = []
for reptile in range(10):
    task_2 = gevent.spawn(Works)
    tasks_list_2.append(task_2)
gevent.joinall(tasks_list_2)
print(list_photo)

work_3 = Queue()
for urls_photo in list_photo:
    work_3.put_nowait(urls_photo)

def Download():
    while not work_3.empty():
        urls_photo = work_3.get_nowait()
        headers_photo = {
            'referer': 'https://www.pixiv.net/artworks/{}'.format(urls_photo[1]),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        res_photo = session.get(urls_photo[0], headers=headers_photo)
        print(res_photo.status_code)
        with open('image/{}'.format(urls_photo[0].replace('https://i.pximg.net/img-original/img/', '').replace('/', '_')), 'wb') as photo:
            photo.write(res_photo.content)
        print('剩余:'+str(work_3.qsize())+'张')

tasks_list_3  = []
for reptile in range(10):
    task_3 = gevent.spawn(Download)
    tasks_list_3.append(task_3)
gevent.joinall(tasks_list_3)

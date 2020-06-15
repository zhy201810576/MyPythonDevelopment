
import requests

# id_author = '2874136'
id_author = '1920354'
ulr_author = 'https://www.pixiv.net/ajax/user/{}/profile/all?lang=zh'.format(id_author)
headers_author = {
    'referer': 'https://www.pixiv.net/users/{}'.format(id_author),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}
session = requests.session()
res_author = session.get(ulr_author, headers=headers_author)
print(res_author.status_code)
json_author = res_author.json()
illusts = json_author['body']['illusts']
userName = json_author['body']['pickup'][0]['userName']
illust_num = len(illusts)
print('画师{0}共有{1}幅作品'.format(userName, illust_num))
for illust in illusts:
    print(illust)

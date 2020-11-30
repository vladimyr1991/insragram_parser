import requests
from json import loads
from requests import get
from bs4 import BeautifulSoup as BS
import time
from random import randrange
import pandas as pd
from datetime import datetime
import re


def get_ulogin_by_uid(user_id):

    print(f'USER ID {user_id}')
    user = {}
    if user_id:
        base_url = "https://i.instagram.com/api/v1/users/{}/info/"
        #valid user-agent
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)'
        }
        try:
            res = requests.get(base_url.format(user_id), headers=headers)
            user_info = res.json()

            user = user_info.get('user', {})
        except Exception as e:
            print("getting user failed, due to '{}'".format(e))
    return user['username']

def get_udata_by_ulogin(login, session):

    print(login)
    # set of regexps
    regex_for_extracting_json = r'{.+}'

    resp = session.get(f'https://instagram.com/{login}/?__a=1/')



    if resp.status_code == 200:

        soup = BS(resp.text, 'html.parser')

        dirty_json_with_info = str(soup.find_all('script')[4])
        clean_json_with_info = re.search(regex_for_extracting_json, dirty_json_with_info)

        # в закрытых аккаунтах нужно смотреть информацию с индексом 3
        if clean_json_with_info == None:
            dirty_json_with_info = str(soup.find_all('script')[3])
            clean_json_with_info = re.search(regex_for_extracting_json, dirty_json_with_info).group(0)

        clean_json_with_info = re.search(regex_for_extracting_json, dirty_json_with_info).group(0)


        full_name = loads(clean_json_with_info)['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']
        num_of_subscribers = loads(clean_json_with_info)['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
        follow = loads(clean_json_with_info)['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']
        posted_media = loads(clean_json_with_info)['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
        external_url = loads(clean_json_with_info)['entry_data']['ProfilePage'][0]['graphql']['user']['external_url']

        result =  {
                'логин':login,
                'название_или_имя_профиля':full_name,
                'количество_подписчиков':num_of_subscribers,
                'количество_постов':posted_media,
                'количество_подписок':follow,
                'ссылка':external_url
            }
        return result
    
    else:
        return {
                'логин':login,
                'название_или_имя_профиля':None,
                'количество_подписчиков':None,
                'количество_постов':None,
                'количество_подписок':None,
                'ссылка':None
            }

def make_data_frame_with_meta_from_list_of_logins(list_of_logins):

    with open('./credentials.json') as f:
        credentials = loads(f.read())
    USERNAME = credentials['username']
    PASSWORD = credentials['password']

    link = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    timestamp = int(datetime.now().timestamp())

    payload = {
        'username': USERNAME,
        'enc_password':
        f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{PASSWORD}',  # <-- note the '0' - that means we want to use plain passwords
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    with requests.Session() as s:
        r = s.get(link)
        csrf = re.findall(r"csrf_token\":\"(.*?)\"", r.text)[0]
        r = s.post(
            login_url,
            data=payload,
            headers={
                "user-agent":
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
                "referer": "https://www.instagram.com/accounts/login/",
                "x-csrftoken": csrf
            })
        print(r.status_code)
        print(r.url)
        print(r.text)
        parsed_results = {'логин':[],
                        'название_или_имя_профиля':[],
                        'количество_подписчиков':[],
                        'количество_постов':[],
                        'количество_подписок':[],
                        'ссылка':[]
                        }

        for ulogin in list_of_logins:

            u_data = get_udata_by_ulogin(ulogin, session = s)

            parsed_results['логин'].append(u_data['логин'])
            parsed_results['название_или_имя_профиля'].append(
                u_data['название_или_имя_профиля'])
            parsed_results['количество_подписчиков'].append(
                u_data['количество_подписчиков'])
            parsed_results['количество_постов'].append(u_data['количество_постов'])
            parsed_results['количество_подписок'].append(
                u_data['количество_подписок'])
            parsed_results['ссылка'].append(u_data['ссылка'])

            # перерывы между парсингом
            var_for_sleep_time = randrange(5, 15, 2)
            time.sleep(var_for_sleep_time)

        parsed_results = pd.DataFrame(parsed_results)

        return parsed_results
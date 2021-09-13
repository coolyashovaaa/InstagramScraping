# Storing data in dictionary

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import pandas as pd
import time


class ProfileRequest:
    def __init__(self, username, driver_path):
        self.username = username
        self.driver_path = driver_path

    def get_dict_response(self):
        browser = webdriver.Chrome(f'{self.driver_path}')
        browser.get(f'https://www.instagram.com/{self.username}/?hl=en')
        source = browser.page_source
        data = bs(source, 'html.parser')
        browser.close()
        body = data.find('body')
        script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
        return json.loads(script.string.split(' = ', 1)[1].rstrip(';'))


class ProfileData:
    def __init__(self, response_dict):
        self.response_dict = response_dict

    def get_profile_inf(self, fields):
        r = self.response_dict['entry_data']['ProfilePage'][0]
        p_inf = {}

        for f in fields:
            if f not in p_inf:
                p_inf[f] = r[f]
            else:
                continue

        return p_inf

    def get_user_inf(self, fields):
        r = self.response_dict['entry_data']['ProfilePage'][0]['graphql']['user']
        u_inf = {}

        for f in fields:
            if f not in u_inf:
                if isinstance(r[f], dict):
                    u_inf[f] = r[f]['count']
                else:
                    u_inf[f] = r[f]
            else:
                continue

        return u_inf

    def get_publications_stats(self, statistic = 'mean'):
        stats = dict.fromkeys({'likes', 'comments', 'video_prop'})
        pubs = self.response_dict['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        if statistic == 'mean':
            func = np.mean
        elif statistic == 'median':
            func = np.median
        else:
            raise ValueError('Invalid statistic type. Expected "mean" or "median"')

        stats['likes'] = func([pubs[i]['node']['edge_liked_by']['count'] for i, p in enumerate(pubs)])
        stats['comments'] = func([pubs[i]['node']['edge_media_to_comment']['count'] for i, p in enumerate(pubs)])
        stats['video_prop'] = func([pubs[i]['node']['is_video'] for i, p in enumerate(pubs)])

        return stats

    def search_bio(self, key_words):
        key_words = [x.lower() for x in key_words]
        bio = self.response_dict['entry_data']['ProfilePage'][0]['graphql']['user']['biography'].lower()
        words = {}

        for k in key_words:
            if k not in words:
                words[k] = k in bio
            else:
                continue

        return words


# Example with 4 shops

shops = ["avocado.ecoo",
         "avoska_store",
         "botavikos",
         "camocvet"]

profile_fields = ['seo_category_infos']
user_fields = ['edge_followed_by', 'edge_follow', 'full_name', 'is_business_account']
bio_key_words = ['уход', 'косметик', 'одежда']

df = pd.DataFrame(columns = ['shop'] + profile_fields + user_fields + bio_key_words)

for i, val in enumerate(shops):
    response = ProfileRequest(f'{shops[i]}', '/Users/coolyashovaaa/Downloads/chromedriver').get_dict_response()
    profile = ProfileData(response)

    df.loc[i, 'shop'] = shops[i]

    df.loc[i, profile_fields[0]] = str(profile.get_profile_inf(profile_fields))

    user_data = profile.get_user_inf(user_fields)

    for u in user_fields:
        df.loc[i, u] = user_data[u]

    bio_data = profile.search_bio(bio_key_words)

    for w in bio_key_words:
        df.loc[i, w] = bio_data[w]

    publ_stats = profile.get_publications_stats("median")

    for s in publ_stats.keys():
        df.loc[i, s] = publ_stats[s]

    time.sleep(1)


# Use @dataclass as data container

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass
class UserDetails:
    biography: str
    edge_followed_by: dict[str, int]
    edge_follow: dict[str, int]
    full_name: str
    highlight_reel_count: int
    is_business_account: bool
    is_professional_account: bool


@dataclass
class User:
    user: UserDetails


@dataclass
class ProfileDetails:
    seo_category_infos: str
    graphql: User


@dataclass
class Profile:
    ProfilePage: list[ProfileDetails]


@dataclass_json
@dataclass
class EntryData:
    entry_data: Profile

# Example

browser = webdriver.Chrome('/Users/coolyashovaaa/Downloads/chromedriver')
browser.get('https://www.instagram.com/avocado.ecoo/?hl=en')
source = browser.page_source
data = bs(source, 'html.parser')
browser.close()
body = data.find('body')
script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
page_json = script.string.split(' = ', 1)[1].rstrip(';')

EntryData.from_json(page_json).entry_data.ProfilePage[0].graphql.user.biography
# '🌱Продукты для здорового питания\n🌱Натуральная косметика\n🌱Бытовая НЕхимия\nС 9:00 до 21:00 без выходных!\n📍ул.
# Н. Ершова, д.62 в, к.2 (ЖК «Арт Сити»)' 




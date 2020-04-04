import collections
import faker
import math
import requests
import time
import warnings

from selenium import webdriver



F = faker.Faker()



class User:
    '''User model

    API:
        - property
            - followers: iterator
            - number_of_followers: int
            - followings: iterator
            - number_of_followings: int
        - function
            - set_info()
            - set_cookies(cookies: dict)
            - set_cookies_from_selenium(webdriver: selenium.webdriver.Remote)
    '''

    _URL_VIDEO = 'https://api.bilibili.com/x/space/arc/search'
    _URL_FOLLOWER = 'https://api.bilibili.com/x/relation/followers'
    _URL_FOLLOWING = 'https://api.bilibili.com/x/relation/followings'

    def __init__(self, id, info=True):
        self.id = int(id)
        self._session = requests.Session()
        self._session.headers.update({
            'host': 'api.bilibili.com',
            'referer': 'https://www.bilibili.com',
            'user-agent': F.user_agent(),
        })
        self.info = None
        info and self.set_info()


    def __repr__(self):
        if self.info:
            return f'<User("{self.info["name"]}") @ LV {self.info["level"]}>'
        else:
            return f'<User({self.id})>'


    @property
    def followers(self):
        '''Iterate all followers from user

        Example:
            >>> for follower in user.followers:
            ...     print(follower)
        '''
        url = self._URL_FOLLOWER
        count = self.number_of_followers
        keys1, key2 = ('data', 'list'), 'mid'
        for page in self._data(url, count, 20, 'desc', 'vmid', keys1, key2):
            for id in page:
                yield User(id, self.info is not None)


    @property
    def number_of_followers(self):
        '''Return the number of followers
        '''
        data = self._data_at(self._URL_FOLLOWER, 1, 20, 'desc', 'vmid')
        return data['data']['total']


    @property
    def followings(self):
        '''Iterate all followings from user

        Example:
            >>> for following in user.followings:
            ...     print(following)
        '''
        url = self._URL_FOLLOWING
        keys1, key2 = ('data', 'list'), 'mid'
        count = self.number_of_followings
        for page in self._data(url, count, 20, 'desc', 'vmid', keys1, key2):
            for id in page:
                yield User(id, self.info is not None)


    @property
    def number_of_followings(self):
        '''Return the number of followings
        '''
        data = self._data_at(self._URL_FOLLOWING, 1, 20, 'desc', 'vmid')
        return data['data']['total']


    def set_info(self):
        '''Set information of current user
        '''
        if not self.info:
            self.info = self._find_info()


    def set_cookies(self, cookies):
        '''Set cookies of current session with `cookies`
        '''
        self._session.cookies.update(cookies)


    def set_cookies_from_selenium(self, webdriver):
        '''Set cookies from `selenium`
        '''
        cookies = webdriver.get_cookies()
        self.set_cookies({item['name']: item['value'] for item in cookies})


    def _data(self, url, count, ps, order, id_name, keys1, key2):
        page_number = math.ceil(count/ps)
        f, g = self._ids_at, self._data_at
        return (
            f(g(url, page+1, ps, order, id_name), keys1, key2)
                for page in range(page_number)
        )


    def _data_at(self, url, page, ps, order, id_name):
        params = dict(ps=ps, pn=page, order=order)
        params[id_name] = self.id
        response = self._session.get(url, params=params)
        return response.json()


    def _ids_at(self, data, keys1, key2):
        try:
            for key in keys1:
                data = data[key]
            for video in data:
                yield video[key2]
        except KeyError:
            warnings.warn('Unauthenticated access cannot get more information, ' \
                'please login by selenium.', Warning)
            return None


    def _find_info(self):
        info = dict()
        # account info
        params = dict(mid=self.id, jsonp='jsonp')
        url = 'https://api.bilibili.com/x/space/acc/info'
        response = self._session.get(url, params=params)
        data = response.json().get('data')
        for key in ('name', 'sex', 'face', 'sign', 'level', 'birthday'):
            info[key] = data.get(key)
        # up status
        url = 'https://api.bilibili.com/x/space/upstat'
        response = self._session.get(url, params=params)
        data = response.json().get('data')
        info['archive_view'] = data.get('archive').get('view')
        info['article_view'] = data.get('article').get('view')
        info['likes'] = data.get('likes')
        # relation status
        params = dict(vmid=self.id, jsonp='jsonp')
        url = 'https://api.bilibili.com/x/relation/stat'
        response = self._session.get(url, params=params)
        data = response.json().get('data')
        info['following'] = data.get('following')
        info['follower'] = data.get('follower')
        # return value
        return info



if __name__ == '__main__':
    myself = User(354576498)
    texts = (
        '开门，社区送温暖 qwq',
        '领得不多，见谅哈～早点休息！',
    )
    gift_num = 5

    browser = webdriver.Firefox()
    browser.get('https://passport.bilibili.com/login')
    input('请扫码登录，成功后回车 >>> ')
    myself.set_cookies_from_selenium(browser)
    for following in myself.followings:
        browser.get(f'https://space.bilibili.com/{following.id}/')
        time.sleep(3)
        live = browser.find_elements_by_class_name('i-live-on')
        if live:
            try:
                live_url = live[0].find_element_by_class_name('i-live-link').get_attribute('href')
                live_id = int(live_url.rsplit('/', 1)[-1])
                response = requests.get(f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={live_id}')
                if response.json()['data']['room_info']['area_name'] == '学习':
                    browser.get(live_url)
                    time.sleep(5)
                    for text in texts:
                        browser.find_element_by_class_name('chat-input.border-box').send_keys(text)
                        time.sleep(3)
                        browser.find_element_by_class_name('txt').click()
                    time.sleep(3)
                    send_url = 'https://api.live.bilibili.com/gift/v2/Live/send'
                    myself._session.headers['host'] = 'api.live.bilibili.com'
                    myself._session.headers['referer'] = live_url
                    csrf = browser.get_cookie('bili_jct')['value']
                    data = dict(
                        uid=myself.id, gift_id=1, ruid=following.id, send_ruid=0,
                        gift_num=gift_num, coin_type='silver', bag_id=0, platform='pc',
                        biz_code='live', biz_id=live_id, rnd=int(time.time()),
                        storm_beat_id=0, metadata='', price=0, csrf_token=csrf, csrf=csrf,
                        visit_id='',
                    )
                    response = myself._session.post(send_url, data=data)
                    if response.json()['msg'] == 'success':
                        print('[成功]', following)
                    else:
                        print('[失败]', following)
            except Exception as e:
                print('[失败]', following, e)

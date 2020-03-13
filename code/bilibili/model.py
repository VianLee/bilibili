#!/usr/bin/python3
__all__ = ('User', 'Video', 'Auto')



import collections
import faker
import math
import requests
import time
import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions



F = faker.Faker()
Comment = collections.namedtuple('Comments', ('content', 'like', 'user_id', 'timestamp'))



class User:
    '''User model

    API:
        - videos: iterator, all Video
    '''
    def __init__(self, id, info=True):
        self.id = id
        self._headers = {
            'host': 'api.bilibili.com',
            'referer': 'https://www.bilibili.com',
            'user-agent': F.user_agent(),
        }
        if info:
            self.info = self._find_info()


    def __repr__(self):
        return f'<User({self.info["name"]}) @ LV {self.info["level"]}>'


    @property
    def video_ids(self):
        for page in self._videos():
            yield from page


    @property
    def videos(self):
        for page in self._videos():
            for id in page:
                yield Video(id)


    def _videos(self, ps=30):
        first_page = self._videos_data_at(1)
        page_info = first_page['data']['page']
        page_number = math.ceil(page_info['count']/ps)
        f, g = self._find_videos, self._videos_data_at
        return (f(g(page+1)) for page in range(page_number))


    def _videos_data_at(self, page, ps=30):
        url = 'https://api.bilibili.com/x/space/arc/search'
        params = dict(mid=self.id, ps=ps, pn=page, order='pubdate')
        response = requests.get(url, params=params, headers=self._headers)
        return response.json()


    def _find_videos(self, data):
        for video in data['data']['list']['vlist']:
            yield video['aid']


    def _find_info(self):
        info = dict()
        # account info
        params = dict(mid=self.id, jsonp='jsonp')
        url = 'https://api.bilibili.com/x/space/acc/info'
        response = requests.get(url, params=params, headers=self._headers)
        data = response.json().get('data')
        for key in ('name', 'sex', 'face', 'sign', 'level', 'birthday'):
            info[key] = data.get(key)
        # up status
        url = 'https://api.bilibili.com/x/space/upstat'
        response = requests.get(url, params=params, headers=self._headers)
        data = response.json().get('data')
        info['archive_view'] = data.get('archive').get('view')
        info['article_view'] = data.get('article').get('view')
        info['likes'] = data.get('likes')
        # relation status
        params = dict(vmid=self.id, jsonp='jsonp')
        url = 'https://api.bilibili.com/x/relation/stat'
        response = requests.get(url, params=params)
        data = response.json().get('data')
        info['following'] = data.get('following')
        info['follower'] = data.get('follower')
        # return value
        return info



class Video:
    '''Video model

    API:
        - comments, iterator, all comments info
    '''
    def __init__(self, id, info=True):
        self.id = id
        self._headers = {
            'host': 'api.bilibili.com',
            'referer': 'https://www.bilibili.com',
            'user-agent': F.user_agent(),
        }
        self._timestamp = int(1000*time.time())
        if info:
            self.info = self._find_info()


    def __repr__(self):
        return f'<Video({self.info["title"]}) @ View {self.info["view"]}>'


    @property
    def comments(self):
        '''
        Format:
            - (content, like, user_id, timestamp)
        '''
        for page in self._comments(): 
            yield from page


    def _comments(self):
        first_page = self._comments_data_at(1)
        if first_page['data']:
            page_info = first_page['data']['page']
            page_number = math.ceil(page_info['count']/page_info['size'])
            f, g = self._find_comments, self._comments_data_at
            return (f(g(page+1)['data']['replies'])
                for page in range(page_number))
        return [[]]


    def _comments_data_at(self, page, root=0, ps=10, sort=2):
        url = 'https://api.bilibili.com/x/v2/reply'
        params = dict(pn=page, type=1, oid=self.id, sort=sort, _=self._timestamp)
        if root:
            url += '/reply'
            params.update(dict(root=root, ps=ps))
        return requests.get(url, params=params, headers=self._headers).json()


    def _find_comments(self, replies, ps=10):
        if replies:
            for reply in replies:
                message = reply['content']['message']
                mid = reply['member']['mid']
                ctime = reply['ctime']
                like = reply['like']
                yield Comment(message, like, mid, ctime)
                rcount = reply['rcount']
                if rcount:
                    for page in range(math.ceil(rcount/ps)):
                        rpid = reply['rpid']
                        data = self._comments_data_at(page+1, rpid, ps)
                        replies = data['data']['replies']
                        yield from self._find_comments(replies)


    def _find_info(self):
        info = dict()
        # video info
        url = 'https://api.bilibili.com/x/web-interface/view'
        response = requests.get(url, params=dict(aid=self.id))
        data = response.json().get('data')
        for key in ('pic', 'title', 'pubdate', 'desc'):
            info[key] = data.get(key)
        info['owner'] = data['owner']['mid']
        # stat info
        stat = data['stat']
        for key in ('view', 'danmaku', 'reply', 'favorite', 'coin', 'share', 'like'):
            info[key] = stat.get(key)
        return info



class Auto:
    _HOME = 'https://www.bilibili.com'
    _SPACE = 'https://space.bilibili.com'


    def __init__(self, login=True, web_driver='Chrome'):
        # set browser
        if isinstance(web_driver, str):
            self._browser = getattr(webdriver, web_driver)()
        elif isinstance(web_driver, webdriver.Remote):
            self._browser = web_driver
        else:
            raise TypeError('Argument `web_driver` has wrong type.')
        # login
        self._goto(self._HOME)
        if login:
            self.login()


    def __repr__(self):
        return f'<Auto @ {hash(self):#x}>'


    def login(self):
        '''Since I am lazy to write this function, you may login your
        Bilibili account manually.
        '''
        while self._browser.find_elements_by_class_name('logout-face'):
            input('(Off-line) Please log in >>> ')
        print('(On-line) You are now logged in.')


    def like_videos_from_user_in_video_comments(self, video_id):
        '''从视频评论区获得用户，点赞其投稿视频
        '''
        users = set()
        v = Video(video_id)
        for comment in v.comments:
            if comment.user_id not in users:
                users.add(comment.user_id)
                self.like_videos_from_user(comment.user_id)


    def like_videos_from_user(self, user_id):
        for video in User(user_id).videos:
            self._goto(self._video_url_from_id(video.id))
            # self._wait(element_to_be_clickable=(By.CLASS_NAME, class_like))
            self.like_this_video()


    def like_this_video(self):
        class_like = 'van-icon-videodetails_like'
        class_flag = 'like.on'
        self._browser.implicitly_wait(10)
        if not self._browser.find_elements_by_class_name(class_flag):
            element = self._browser.find_element_by_class_name(class_like)
            element.click()


    def _goto(self, url):
        self._browser.get(url)


    def _wait(self, timeout=5, poll_frequency=0.5, **kwargs):
        '''Web driver wait.

        Argument:
            - timeout: [int, float]
            - poll_frequency: [int, float]

        Example:
            >>> self._wait(element_to_be_clickable=(By.ID, '...'))
        '''
        wait =  WebDriverWait(self._browser, timeout, poll_frequency)
        for key, val in kwargs.items():
            wait.until(getattr(expected_conditions, key)(val))


    def _user_url_from_id(self, id):
        return self._SPACE + f'/{id}'


    def _video_url_from_id(self, id):
        return self._HOME + f'/av{id}'



if __name__ == '__main__':
    u = User(546195)
    vs = u.videos
    print(next(vs))

    v = Video(70885948)
    cs = v.comments
    print(next(cs))
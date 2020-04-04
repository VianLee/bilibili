__all__ = ('Session', )



import faker
import functools
import requests

from selenium import webdriver



F = faker.Faker()



class Session:
    '''Bilibili Session model

    API:
        - value
            - session
            - browser
        - property
            - is_login
        - function
            - set_headers(headers: dict)
            - set_cookies(cookies: dict)
            - set_cookies_from_selenium(webdriver: selenium.webdriver.Remote)
            - set_user_agent(user_agent: dict)
            - login_by_selenium(name: str)
            + login_by_password(username: str, password: str)
        - decorator
            - required_login(func)
    '''

    def __init__(self, login_by='selenium'):
        self.session = requests.Session()
        self.session.headers.update({
            'host': 'api.bilibili.com',
            'referer': 'https://www.bilibili.com',
            'user-agent': F.user_agent(),
        })
        self.browser = None
        self._login = False
        self._login_by = getattr(self, f'login_by_{login_by}')


    @property
    def is_login(self):
        return self._login


    def set_headers(self, headers):
        '''
        Argument:
            - headers: dict
        '''
        self.session.headers.update(headers)


    def set_cookies(self, cookies):
        '''
        Argument:
            - cookies: dict
        '''
        self.session.cookies.update(cookies)


    def set_cookies_from_selenium(self, webdriver):
        '''Set cookies from `selenium`
        '''
        cookies = webdriver.get_cookies()
        self.set_cookies({item['name']: item['value'] for item in cookies})


    def set_user_agent(self, user_agent=None):
        '''
        Argument:
            - user_agent: str
        '''
        self.set_headers({'user-agent': (user_agent or F.user_agent())})


    def login_by_selenium(self, name='Firefox'):
        '''
        Argument:
            - name: str, selenium.webdriver.`name`
        '''
        self.browser = getattr(webdriver, name)()
        self.browser.get('https://passport.bilibili.com/login')
        input('Please login in >>> ')
        self.set_cookies_from_selenium(self.browser)
        self._login = True


    def login_by_password(self, username, password):
        '''
        References:
            - https://github.com/Hsury/Bilibili-Toolkit
            - https://github.com/apachecn/BiliDriveEx
        '''
        raise NotImplementedError


    def required_login(self, *args, **kwargs):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._login:
                    self._login_by(*args, **kwargs)
                return func(*args, **kwargs)
            return wrapper
        return decorator

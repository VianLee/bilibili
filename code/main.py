#!/usr/bin/python3
from time import sleep
from selenium import webdriver

from bilibili.auto import tests

Auto = tests.Auto

from experimental_features import LiveByArea


if __name__ == '__main__':
    # IPython >>> %run -i main.py
    ## Cache the webdriver
    if 'browser' not in locals():
        browser = webdriver.Firefox()
    else:
        exit(0)
    # a = Auto(web_driver=browser, login=True)

    # 直播间留言
    browser.get('https://passport.bilibili.com/login')
    input('Please login >>> ')
    live = LiveByArea(27)
    urls = dict()
    tag = 'room-owner-username.live-skin-normal-a-text.dp-i-block.v-middle'
    for url in live.urls:
        if url in urls:
            continue
        else:
            urls[url] = None
        try:
            browser.get(url)
            sleep(5)
            user_name = browser.find_elements_by_class_name(tag)[0].text
            texts = (
                f'晚饭时间！{user_name} 记得休息呀～',
            )
            for text in texts:
                browser.find_element_by_class_name('chat-input.border-box') \
                    .send_keys(text)
                sleep(3)
                browser.find_element_by_class_name('txt') \
                    .click()
        except Exception as e:
            print(e)
            continue
        sleep(3)

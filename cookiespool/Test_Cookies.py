'''
title:测试模块，检测cookies的可用性
'''
import json
import requests
from requests.exceptions import ConnectionError
from cookiespool.Redis_DB import *
from cookiespool.Settings import *


class ValidTester(object):
    '''父类，初始化一些变量'''
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)


    #  子类中重写test方法就可以了，这样可以提高这个cookies的通用性，要检测哪个网站就直接写在test方法中就可以了
    def test(self, username, cookies):
        raise NotImplementedError
    
    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.items():
            self.test(username, cookies)


class WeiboValidTester(ValidTester):
    def __init__(self, website='weibo'):
        ValidTester.__init__(self, website)
    
    def test(self, username, cookies):
        print('正在测试Cookies', '用户名', username)
        # 首先将Cookies转化为字典，检测cookies的格式，如果没有问题就直接用来进行检测，如果有问题就直接删除
        try:
            cookies = json.loads(cookies)
        except json.decoder.JSONDecodeError:
            print('Cookies不合法', username)
            self.cookies_db.delete(username)
            print('删除Cookies', username)
            return
        try:
            # 定义要检测的网站，这里是写在config.py中的
            test_url = TEST_URL_MAP[self.website]
            # 设置了超时时间以及禁止重定向
            response = requests.get(test_url, cookies=cookies, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print('Cookies有效', username)
            else:
                print(response.status_code, response.headers)
                print('Cookies失效', username)
                self.cookies_db.delete(username)
                print('删除Cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)

if __name__ == '__main__':
    WeiboValidTester().run()
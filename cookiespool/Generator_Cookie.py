'''
title:生成器模块,用户生成cookies
'''
import json
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cookiespool.Settings import *
from cookiespool.Redis_DB import RedisClient
from login.weibo.cookies import WeiboCookies
class CookiesGenerator(object):
    def __init__(self, website='default'):
        """
        父类, 初始化一些对象
        website: 名称
        browser: 浏览器, 若不使用浏览器则可设置为 None
        """
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
        self.init_browser()

    def __del__(self):
        self.close()
    
    def init_browser(self):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :return:
        """
        if BROWSER_TYPE == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps[
                "phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
            self.browser.set_window_size(1400, 500)
        elif BROWSER_TYPE == 'Chrome':
            self.browser = webdriver.Chrome()
    
    def new_cookies(self, username, password):
        """
        新生成Cookies，子类需要重写
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError
    
    def process_cookies(self, cookies):
        """
        处理Cookies
        :param cookies:
        :return:
        """
        dict = {}
        for cookie in cookies:
            dict[cookie['name']] = cookie['value']
        return dict
    
    def run(self):

        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()
        # 遍历账号的Hash,对比Cookies总的Hash多了哪些还没有生成cookies的账号，然后将剩余的账号遍历，再去生成新的cookies
        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.accounts_db.get(username)
                print('正在生成Cookies', '账号', username, '密码', password)
                result = self.new_cookies(username, password)
                # 这里定义状态码为1表示成功获取Cookies，状态码为2表示用户名或者密码错误，然后将密码错误的账号从数据库中删除
                # 这里的状态是在模拟登陆中定义得到的,coutent表示的是每个状态码的具体表示信息
                if result.get('status') == 1:
                    # 调用process_cookies方法处理cookies，这里状态码为1的时候返回的content表示的就是cookies
                    cookies = self.process_cookies(result.get('content'))
                    print('成功获取到Cookies', cookies)
                    # 如果获取到新生成的cookies就将其保存到数据库中
                    if self.cookies_db.set(username, json.dumps(cookies)):
                        print('成功保存Cookies')
                # 密码错误，移除账号
                elif result.get('status') == 2:
                    print(result.get('content'))
                    if self.accounts_db.delete(username):
                        print('成功删除账号')
                else:
                    print(result.get('content'))
    
    def close(self):
        """
        关闭
        :return:
        """
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, website='weibo'):
        # 继承自CookiesGenerator这个类
        # 初始化站点名称和使用的浏览器
        CookiesGenerator.__init__(self, website)
        self.website = website
    
    def new_cookies(self, username, password):
        # 调用模拟登陆，得到生成的Cookie和用户名
        return WeiboCookies(username, password, self.browser).main()


if __name__ == '__main__':
    generator = WeiboCookiesGenerator()
    generator.run()

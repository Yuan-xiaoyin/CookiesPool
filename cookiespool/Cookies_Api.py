import json
from flask import Flask, g
from cookiespool.Settings import *
from cookiespool.Redis_DB import *

__all__ = ['app']

app = Flask(__name__)

@app.route('/')
def index():
    return '<h2>Welcome to Cookie Pool System</h2>'


def get_conn():

    for website in GENERATOR_MAP:
        print(website)
        # hasattr:这里是判断一个对象里面是否有website属性或方法
        if not hasattr(g, website):
            # setattr(),给对象的属性赋值，如果不存在此属性，则先创建再赋值
            # eval()：将字符串当成表达式计算并返回结果,这里就是将eval后面的值付给website+'_cookies'
            setattr(g, website + '_cookies', eval('RedisClient' + '("cookies", "' + website + '")'))
            setattr(g, website + '_accounts', eval('RedisClient' + '("accounts", "' + website + '")'))
    # g对象用来保存用户的数据，在全局都是可用的,相当于global
    return g


@app.route('/<website>/random')
def random(website):
    # 获取随机的Cookie, 访问地址如 /weibo/random
    g = get_conn()
    # getattr()返回一个对象的属性的值，这里就是返回get_conn方法里面设置的值
    cookies = getattr(g, website + '_cookies').random()
    return cookies


@app.route('/<website>/add/<username>/<password>')
def add(website, username, password):
    """
    添加用户, 访问地址如 /weibo/add/user/password
    :param website: 站点
    :param username: 用户名
    :param password: 密码
    :return: 
    """
    g = get_conn()
    print(username, password)
    getattr(g, website + '_accounts').set(username, password)
    return json.dumps({'status': '1'})


@app.route('/<website>/count')
def count(website):
    """
    获取Cookies总数
    """
    g = get_conn()
    count = getattr(g, website + '_cookies').count()
    return json.dumps({'status': '1', 'count': count})


if __name__ == '__main__':
    app.run(host='0.0.0.0')

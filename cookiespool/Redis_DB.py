'''
title:redis数据库模块：定义一些数据库的操作方法
'''
import random
import redis
from cookiespool.Settings import *
class RedisClient(object):
    def __init__(self, type, website, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        # 初始化Redis连接
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = type
        self.website = website

    def name(self):
        # 获取Hash的名称,分别代表类型和站点名称，这样方便扩展其他的网站存储
        return "{type}:{website}".format(type=self.type, website=self.website)

    def set(self, username, value):
        # hset(name,key,value):向键名为name的散列表中添加映射，这里就是想键名为self.name的键名中添加映射键名username,映射键值value
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        # hget返回键名为self.name的散列表中各个键对应的值
        return self.db.hget(self.name(), username)

    def delete(self, username):
        # hdel:在键名为self.name的散列表中删除键名为username的映射
        return self.db.hdel(self.name(), username)

    def count(self):
        # hlen():从键名为name的散列表中获取映射个数
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        此方法与接口模块对接，获取随机的cookies
        """
        return random.choice(self.db.hvals(self.name()))
    def usernames(self):
        # 从键名为self.name中的散列表中获取映射个数
        return self.db.hkeys(self.name())

    def all(self):
        # 从键名为self.name的散列表中获取所有的键值对
        return self.db.hgetall(self.name())
# if __name__ == '__main__':
#     conn = RedisClient('accounts', 'weibo')
#     result = conn.set('hell2o', 'sss3s')
#     print(result)

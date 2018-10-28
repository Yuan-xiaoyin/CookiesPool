'''
title:调度模块，采用多进程的方式调用各个模块
'''
import time
from multiprocessing import Process
from cookiespool.Cookies_Api import app
from cookiespool.Settings import *
from cookiespool.Generator_Cookie import *
from cookiespool.Test_Cookies import *


class Scheduler(object):
    @staticmethod
    def valid_cookie(cycle=CYCLE):
        while True:
            print('Cookies检测进程开始运行')
            try:
                for website, cls in TESTER_MAP.items():
                    tester = eval(cls + '(website="' + website + '")')
                    tester.run()
                    print('Cookies检测完成')
                    del tester
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)
    
    @staticmethod
    def generate_cookie(cycle=CYCLE):
        while True:
            print('Cookies生成进程开始运行')
            try:
                # 在config中配置了GENERATOR_MAP与TESTER_MAP。是产生器类和测试模块类
                for website, cls in GENERATOR_MAP.items():
                    # 动态的构建各个类的对象
                    generator = eval(cls + '(website="' + website + '")')
                    # 对象调用run方法运行各个模块
                    generator.run()
                    print('Cookies生成完成')
                    generator.close()
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)
    
    @staticmethod
    def api():
        print('API接口开始运行')
        app.run(host=API_HOST, port=API_PORT)
    
    def run(self):
        # 在config中还配置了API_PRICESS,GENERATOR_PROCESS.VALID_PROCESS各个模块的开关，可以控制进程的开启和关闭
        # 这里调用的multiprocessing中的process类实现多进程，使各个模块运行不受影响
        if API_PROCESS:
            api_process = Process(target=Scheduler.api)
            api_process.start()
        
        if GENERATOR_PROCESS:
            generate_process = Process(target=Scheduler.generate_cookie)
            generate_process.start()
        
        if VALID_PROCESS:
            valid_process = Process(target=Scheduler.valid_cookie)
            valid_process.start()

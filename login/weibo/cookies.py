import time
from io import BytesIO
from PIL import Image
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import abspath, dirname

TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'


class WeiboCookies():
    def __init__(self, username, password, browser):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        # delete_all_cookies:删除浏览器中所有cookies
        self.browser.delete_all_cookies()
        #用设定的浏览器去访问定义uel
        self.browser.get(self.url)
        # 输入用户名和密码,并点击登陆
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        submit.click()
    
    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                # 判断页面中是否存在errorMsg元素的id，就是判断是否用户名或者密码错误
                EC.text_to_be_present_in_element((By.ID, 'errorMsg'), '用户名或密码错误'))
        except TimeoutException:
            return False
    
    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        # try:
            # return bool(
                # WebDriverWait(self.browser, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'drop-title'))))
            # return bool(WebDriverWait(self.browser,5).until(self.browser.current_url!=self.url))
        # except TimeoutException:
            # return False
        # 判断是否登陆成功，我这里是在验证码识别之后2秒内看看url是不是有变化了，如果有表示登陆成功
        # 这样做很不严谨，还是应该向上面那样判断是否某个元素出现在网页内比较好
        # 这样做可能受到网速的影响,所以我在这里多等了几秒,当大量的账号密码登陆时采用上面那种方法比较好
        successful_url='https://m.weibo.cn/'
        time.sleep(5)
        if self.browser.current_url == successful_url:
            return True
        return False
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        global img
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('未出现验证码')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha
    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False
    def same_image(self, image, template):
        """
        识别相似验证码
        :param image: 待识别验证码
        :param template: 模板
        :return:
        """
        # 相似度阈值
        threshold = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素是否相同
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        print(result)
        if result > threshold:

            print('成功匹配')
            return True
        return False
    def detect_image(self, image):
        """
        匹配图片
        :param image: 图片
        :return: 拖动顺序
        """
        for template_name in listdir(TEMPLATES_FOLDER):
            print('正在匹配', template_name)
            template = Image.open(TEMPLATES_FOLDER + template_name)
            if self.same_image(image, template):
                # 返回顺序
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers
    def move(self, numbers):
        """
        根据顺序拖动
        :param numbers:
        :return:
        """
        # 获得四个按点
        try:
            circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
            dx = dy = 0
            for index in range(4):
                circle = circles[numbers[index] - 1]
                # 如果是第一次循环
                if index == 0:
                    # 点击第一个按点
                    ActionChains(self.browser) \
                        .move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size['height'] / 2) \
                        .click_and_hold().perform()
                else:
                    # 小幅移动次数
                    times = 30
                    # 拖动
                    for i in range(times):
                        ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                        time.sleep(1 / times)
                # 如果是最后一次循环
                if index == 3:
                    # 松开鼠标
                    ActionChains(self.browser).release().perform()
                else:
                    # 计算下一次偏移
                    dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                    dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']
        except:
            return False
    
    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        # 这里调用的selenium中browser的get_cookies方法获取网页中的cookies
        # 有些时候获取不完整，还要做进一步的优化
        return self.browser.get_cookies()
    def main(self):
        """
        破解入口
        :return:
        """
        # 定义获取的状态码，1表示成功登陆，2表示用户名或者密码错误，3表示登陆失败
        self.open()
        if self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        # 获取验证码图片
        image = self.get_image('captcha.png')
        numbers = self.detect_image(image)
        self.move(numbers)
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        # 状态码为3表示登陆失败
        else:
            return {
                'status': 3,
                'content': '登录失败'
            }
# if __name__ == '__main__':
#     result = WeiboCookies('14773427930', 'x6pybpakq1').main()
#     print(result)

# -*- coding: utf-8 -*-
# @Time : 2020/7/19 21:38
# @Author : JACKHEN
# @Site : 武汉理工教务管理系统登录,获取登陆后的cookie,以及选课系统的cookie
# @File : wutjwc_login.py
# @Software: PyCharm

import random
import hashlib
import requests
from lxml import etree
from selenium import webdriver



class WutJwcLogin():

    def __init__(self,usernamne,password):
        self.usernamne = usernamne
        self.password = password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'http://sso.jwc.whut.edu.cn/Certification/toLogin.do',
            "Connection": "keep-alive"
        }
        self.sess = requests.session()
        # 登陆后 主页的cookie
        self.login_cookie_str = ""
        # 选课系统的cookie
        self.xk_cookie_str = ""

    def login(self):
        """
        返回登陆后的cookie
        :return: cookie
        """
        username = self.usernamne
        password = self.password
        print("账号: {} 密码:{}".format(len(username),len(password)))
        url_login = 'http://sso.jwc.whut.edu.cn/Certification/login.do'
        # 登陆需要发送的数据
        post_data = {
            'userName': username, # 账号
            'password': password, # 密码
            'type': 'xs',
            'MsgID': "",
            "KeyID": "",
            "rnd": "",  #
            "UserName": "",
            "Password": "",
            "return_EncData": "",
            "code": "",  #
            "userName1": "",  # 加密参数1
            "password1": "",  # 加密参数2
            "webfinger": "",  # 浏览器指纹,建议一个账号设置一个浏览器指纹
        }
        # 教务管理系统通过md5和sha1进行加密
        m = hashlib.md5()
        m.update(username.encode("utf8"))
        post_data['userName1'] = m.hexdigest()
        m = hashlib.sha1()
        m.update((username + password).encode("utf8"))
        post_data['password1'] = m.hexdigest()

        # rnd加密参数
        page = self.sess.get(url="http://sso.jwc.whut.edu.cn/Certification/toLogin.do", headers=self.headers).text
        html = etree.HTML(page)
        rnd = html.xpath('//*[@id="rnd"]/@value')[0]
        post_data['rnd'] = rnd

        # webfinger
        post_data['webfinger'] = self.get_webfigner()
        # code 根据webfinger获取
        post_data['code'] = self.get_code(post_data['webfinger'])

        # 发送登陆请求
        res = self.sess.post(url_login, data=post_data, headers=self.headers)

        # 判断是否登陆成功,登陆失败返回false
        html = etree.HTML(res.text)
        # 页面仍有账号输入框,说明登陆失败
        if len(html.xpath('//input[@name="userName"]')): return False

        # 登陆成功.获取登陆后的cookie
        if res.cookies:
            cookies = requests.utils.dict_from_cookiejar(res.cookies)
            # 将cookies字典转为字符串
            for key in cookies.keys():
                self.login_cookie_str += key +"="+cookies[key]+";"
            return self.login_cookie_str

        # 没有cookie
        else: return False

    def get_xk_cookie(self):
        """
        获取选课系统的cookie
        :return:
        """

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        mobile_emulation = {"deviceMetrics": {"width": 1050, "height": 840, "pixelRatio": 3.0},
                            "userAgent": user_agent,
                            }
        options.add_experimental_option('mobileEmulation', mobile_emulation)
        options.add_argument('--headless')

        self.browser = webdriver.Chrome(chrome_options=options)
        # 因为添加cookie要先请求一下要添加的网站,否则无法添加
        self.browser.get("http://218.197.102.183/Course")
        for item in self.get_cookie_list():
            print(item)
            self.browser.add_cookie(item)
        self.browser.get("http://218.197.102.183/Course")
        # 截图查看结果
        self.browser.get_screenshot_as_file("seleScreen.png")

        # 获取浏览器cookie
        cookies = self.browser.get_cookies()
        # 通过name和value进行取值
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        # 转为字符串
        self.xk_cookie_str = '; '.join(item for item in cookie)

        return self.xk_cookie_str


    def get_cookie_list(self):
        """
        将cookie字符串转换成字典数字,方便selemiun添加cookie
        :return:
        """
        cookiesList = []
        if not self.login_cookie_str:
            self.login()
        str = self.login_cookie_str
        for item in str.split(";"):
            if item != "":
                dc = {}
                print(item)
                key, value = item.split("=")
                dc["name"] = key.replace(" ","")
                dc["value"] = value.replace(" ","")
                cookiesList.append(dc)
        return cookiesList

    def get_webfigner(self):
        """
        浏览器指纹,只要位数对上了就行
        :return: webfigner
        """
        ls = (
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v',
            'w',
            'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
        str = ""
        for temp in range(32):
            str += ls[random.randint(0, 35)]
        return str

    def get_code(self,webfinger):
        """
        通过webfinger获取code
        :param webfinger:
        :return:
        """
        code_url = "http://sso.jwc.whut.edu.cn/Certification/getCode.do"
        data = {
            'webfinger': webfinger
        }
        code = self.sess.post(code_url, headers=self.headers, data=data).text
        return code

    def fetch_proxy(self):
        """
        获取代理ip,返回的是一个字典
        格式: {http:12.34.56.78:91011,https:12.34.56.78:91011,}
        :return:
        """
        res = requests.get("http://api.xiequ.cn/VAD/GetIp.aspx?act=get&num=1&time=30&plat=0&re=0&type=0&so=1&ow=1&spl=1&addr=&db=1",timeout=2).json()
        dc = {}
        dc['http'] = res['data'][0]['IP'] + ":{}".format(res['data'][0]['Port'])
        dc['https'] = res['data'][0]['IP'] + ":{}".format(res['data'][0]['Port'])
        return dc

def test_un():
    """
    测试账号是否可用
    :return:
    """
    test_un_list = []
    with open('account.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            temp_list = line.split("\t")
            if line !="" and len(temp_list) == 2 :
                un, pwd =temp_list
                if un not in test_un_list: login_spider = WutJwcLogin(un.replace(" ",""),pwd.replace("\n",""))
                else: continue
                if login_spider.login() :
                    test_un_list.append(un)
                    print("成功测试：{}".format(un))
                    with open("test_account.txt","a",encoding="utf8")as f:
                        f.write(un+"\t"+pwd)

def main():
    """
    主类,登陆不同账号,获取选课系统的cookie,并存储到mongoDB
    :return:
    """
    pass


if __name__ == '__main__':
    main()








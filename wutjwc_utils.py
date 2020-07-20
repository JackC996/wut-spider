#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/7/20 18:29
# @Author : JACKHEN
# @Site :  wut教务管理系统工具
# @File : wutjwc_utils.py
# @Software: PyCharm

import requests
from selenium import webdriver

def get_xk_cookie(login_cookie_str):
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

    browser = webdriver.Chrome(chrome_options=options)
    # 因为添加cookie要先请求一下要添加的网站,否则无法添加
    browser.get("http://218.197.102.183/Course")
    for item in get_cookie_list(login_cookie_str):
        print(item)
        browser.add_cookie(item)
    browser.get("http://218.197.102.183/Course")
    # 截图查看结果
    browser.get_screenshot_as_file("seleScreen.png")

    # 获取浏览器cookie
    cookies = browser.get_cookies()
    # 通过name和value进行取值
    cookie = [item["name"] + "=" + item["value"] for item in cookies]
    # 转为字符串
    xk_cookie_str = '; '.join(item for item in cookie)

    return xk_cookie_str


def get_cookie_list(login_cookie_str):
    """
    将cookie字符串转换成字典数字,方便selemiun添加cookie
    :return:
    """
    cookiesList = []
    if not login_cookie_str:
        return "cookie为空"
    str = login_cookie_str
    for item in str.split(";"):
        if item != "":
            dc = {}
            print(item)
            key, value = item.split("=")
            dc["name"] = key.replace(" ", "")
            dc["value"] = value.replace(" ", "")
            cookiesList.append(dc)
    return cookiesList


def fetch_proxy():
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
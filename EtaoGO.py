#!/usr/bin/env python
# encoding: utf-8

#
# 菜鸡,请大神们指点下.
#
"""
@version: ??
@author: lvusyy
@license: Apache Licence
@contact: lvusyy@gmail.com
@site: https://github.com/lvusyy/
@software: PyCharm
@file: EtaoGo.py
@time: 2017/11/10 1:23
"""
import json
import re
import time

import os
from selenium import webdriver
import requests
import sys
import configparser

sys.path.append(os.path.dirname(__file__))


pinTuanurls = {}


class EtaoGo(object):

    def __init__(self, youName, url=''):
        self.youName = youName
        self.url = url
        self.webclient = webdriver.Chrome(port=9515)

    def waitElementRady(self): #等待元素加载完成,最好里面加个条件防止无限循环的出现
        try:
            return self.webclient.find_element_by_class_name("act-btn-single")
        except BaseException:
            return self.waitElementRady()

    def shuaIt(self, url): #开刷
        self.url = url
        self.webclient.get(self.url)

        bt = self.waitElementRady()

        bt.click()
        try:
            input_name = self.webclient.find_element_by_xpath(
                r'//*[@id="draw-popup"]/div[2]/div[1]/div[2]/div[3]/input')
        except Exception as e:
            print(e)
            time.sleep(1)
            input_name = self.webclient.find_element_by_xpath(
                r'//*[@id="draw-popup"]/div[2]/div[1]/div[2]/div[3]/input')
        else:
            input_name.send_keys(self.youName)

        submitBt = self.webclient.find_element_by_xpath(
            r'//*[@id="draw-popup"]/div[2]/div[1]/div[3]/div/div')
        submitBt.click()


class Spider(object):
    def __init__(self, url):
        self.url = url
        self.spider = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        self.spider.headers = self.headers

    def getContent(self, url):
        if not url:
            return False
        try:
            return self.spider.get(url).text
        except Exception as e:
            print(u"打开赚客吧抱团页面出错")
            return False

    def getMaxPage(self, content):
        '共 9 页'
        content = content.replace(" ", "")#搜索文字 看一共多少页
        ret = re.search(u'共(\d*)页', content)
        if ret:
            print(ret.group())
            return ret.group(1)

    def _etaotargetUrl(self, content):
        ret = re.findall(
            r'(http://drfhj.*[a-zA-Z0-9]{32,50})" target="',#正确的是32位长度,
            content)
        if ret:
            return ret

    def getEtaoTargetUrl(self):
        'http://drfhj.com/my.htm?code=ZZA1llKN2T5ws6X3vHAAJsemAB6bPD77'
        '                             n4esFEwIKVOl8jSCMm1H0AWxNnmSlrQ5'
        for _url in self.url:
            content = self.getContent(_url)
            if not content:
                continue
            page = self.getMaxPage(content)
            if page:
                for _pageNow in range(1, int(page)):

                    ret = re.findall(
                        r"(http://www\.zuanke8\.com/thread\-\d+\-)", _url)
                    if ret:
                        _nowurl = ret[0] + str(_pageNow) + '-1.html'
                        content = self.getContent(_nowurl)
                        print(_nowurl)
                        time.sleep(0.2)
                        if not content:
                            continue
                        etaoUrl = self._etaotargetUrl(content)
                        time.sleep(0.2)
                        if etaoUrl and isinstance(etaoUrl, list):
                            for i in etaoUrl:
                                pinTuanurls[i] = 0
                        elif etaoUrl and isinstance(etaoUrl, str):
                            pinTuanurls[etaoUrl] = 0
                        time.sleep(0.2)
                    else:
                        print(u"传递过来的网页不匹配过滤规则.必须失败!")
                        exit(0)

        print(u"解析完成了.共{maxEtaoUrl}条连接".format(maxEtaoUrl=len(pinTuanurls)))
        with open("pintuanurls.json", 'w') as f:
            json.dump(pinTuanurls, f, ensure_ascii=False)



spiderMainUrls = []

# load users



def main(forceUpdate=False):

    users, _isForceUpdateEtaoUrl = [], ''#配置文件相关
    if not os.path.exists('config.ini'):
        conf = configparser.ConfigParser()
        try:
            conf["DEFAULT"] = {"def": '0'}
            conf['users'] = {}
            conf['users']['user'] = 'userName1,userName2'
            conf['users']['isForceUpdateEtaoUrl'] = '0'
            with open('config.ini', 'w') as f:
                conf.write(f)
                f.flush()

        except Exception as e:
            print(e)
            os.remove('config.ini')
            return

    conf = configparser.ConfigParser()#配置文件相关
    conf.read('config.ini')
    _users = conf.get(conf.sections()[0], 'user')
    _isForceUpdateEtaoUrl = conf.get("users", 'isForceUpdateEtaoUrl')

    if _users and _isForceUpdateEtaoUrl:
        users = str(_users).split(",")
        _isForceUpdateEtaoUrl = int(_isForceUpdateEtaoUrl)

    forceUpdate = False if _isForceUpdateEtaoUrl == 0 else True
    names = users

    if not names:
        print(u"读取配置文件出错,退出")
        return

    if names[0] == 'userName1':
        _name = input(u"请输入你的淘宝用户名:")
        if _name:  # 不检查错误
            names[0] = _name
            names[1] = ''
    elif names[1] == 'userName2':
        names[1] = ''

    main_urls=['http://www.zuanke8.com/thread-4456340-1-1.html','http://www.zuanke8.com/thread-4423688-1-1.html']
    # main_urls = ['http://www.zuanke8.com/thread-4423688-1-1.html', '']

    # names=['dengyangpp','sky0910104475']
    zkbSpider = Spider(main_urls)

    filename = "pintuanurls.json"
    global pinTuanurls
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            pinTuanurls = json.load(f)

    else:
        zkbSpider.getEtaoTargetUrl()
        # t1 = threading.Thread(target=zkbSpider.getEtaoTargetUrl, )
        # t1.setDaemon(False)
        # # t1.join()
        #
        # t1.run()

    if forceUpdate:
        zkbSpider.getEtaoTargetUrl()
        # t1 = threading.Thread(target=zkbSpider.getEtaoTargetUrl,)
        # t1.setDaemon(False)
        # t1.join()

        # t1.run()

    users = []
    pass_urls = []

    if os.path.exists("pass.json"):
        with open('pass.json', 'r') as f:
            etaopass = json.load(f)
        for i in etaopass:
            if i in pinTuanurls:
                pinTuanurls.pop(i)

    if len(pinTuanurls) >= 3:
        for name in names:
            if name:
                etg = EtaoGo(name)
                etg.webclient.implicitly_wait(7)
                users.append(etg)
                time.sleep(3)

        for etaourl in pinTuanurls.keys():
            for user in users:
                user.shuaIt(etaourl)
                time.sleep(.8)
                pass_urls.append(etaourl)

            with open("pass.json", 'w') as f:#把刷过的连接存到新json文件中
                json.dump(pass_urls, f, ensure_ascii=False)

        for user in users:
            user.webclient.close()#关闭退出 执行到这里意味着都执行用户都刷完了
            user.webclient.quit()

    print("一淘连接数不够3条")


if __name__ == "__main__":
    main()

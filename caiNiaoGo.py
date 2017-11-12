#!/usr/bin/env python3
# encoding: utf-8


"""
@version: ??
@author: lvusyy
@license: Apache Licence
@contact: lvusyy@gmail.com
@site: https://github.com/lvusyy/
@software: PyCharm
@file: caiNiaoGO.py
@time: 2017/11/12 12:16
"""

#!/usr/bin/env python
# encoding: utf-8

import json
import re
import time

import os

import threading
import urllib.parse as urllib

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
        self.webclient = webdriver.Chrome()
        self.webclient.set_window_size(600,800)
    def waitElementRady(self, times=0):
        try:
            return self.webclient.find_element_by_xpath(
                '/html/body/div/div[1]/div[3]/input')
        except BaseException:
            time.sleep(0.2)
            if times > 3:  # 失败3次就放弃
                return False
            return self.waitElementRady(times + 1)

    def shuaIt(self, url, maxTry=0):
        if maxTry >= 3:  # 尝试超过3次的.必然失败
            return

        url = urllib.unquote(url)
        self.url = url
        self.webclient.get(url)
        bt = self.waitElementRady()
        if bt:
            bt.click()
        else:
            return
        try:
            input_name = self.webclient.find_element_by_xpath(
                r'/html/body/div/div[1]/div[3]/input')
            input_name.send_keys(self.youName)
            submitBt = self.webclient.find_element_by_xpath(
                r'/html/body/div/div[1]/div[4]')
            submitBt.click()
        except BaseException:
            return self.shuaIt(url, maxTry=maxTry + 1)

        time.sleep(1.2)


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
            print(u"打开赚客吧互助页面出错")
            return False

    def getMaxPage(self, content):
        '共 9 页'
        content = content.replace(" ", "")
        ret = re.search(u'共(\d*)页', content)
        if ret:
            print(ret.group())
            return ret.group(1)

    def _useCaiNiaoIdmakeUrl(self,content):
        urls = []
        # url = 'http://www.zuanke8.com/thread-4470619-1-1.html'
        urla = 'https://page.cainiao.com/guoguo/lottery-card-double11/friend.html?nick=make!t&uid='
        ret = re.findall(r'&uid=(\d+)', content)
        for i in ret:
            urls.append(urla + str(i))

        return urls

    def _etaotargetUrl(self, content):
        'https://page.cainiao.com/guoguo/lottery-card-double11/friend.html?nick=m**iang8911&uid=733028254'
        cainaoUrls = []
        rules = [
            r'https?://suo\.im/[a-zA-Z0-9]{6,9}',
            r'(https?://page\.cainiao\.com/guoguo/lottery-card-double11/friend\.html\?nick=.+&uid=[0-9]{9,12})'] #必须有uid不然无法提交的.
        for i in rules:
            ret = re.findall(i, content)
            if ret:
                if isinstance(ret[0], tuple):
                    _tmpList = []
                    for _t in ret:
                        _tmpList.append(_t[0])
                    ret = _tmpList

                for _url in ret: #去除带 target....的多余数据
                    _url=_url.split('"')
                    if _url:
                        _url=_url[0]
                    cainaoUrls.append(_url.replace('amp;',''))
                # cainaoUrls.extend(ret)
        return cainaoUrls


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
                        etaoUrl1 = self._useCaiNiaoIdmakeUrl(content)
                        if etaoUrl1:
                            etaoUrl.extend(etaoUrl1)

                        time.sleep(0.2)
                        if etaoUrl and isinstance(etaoUrl, list)  :
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


def go_(name, urls):
    etg = EtaoGo(name)
    etg.webclient.implicitly_wait(7)
    count = 0
    pass_urls = []
    # print(name,urls)
    for etaourl in urls.keys():
        print("进程 {name} 准备点击 {url}".format(name=etg.youName, url=etg.url))
        etg.shuaIt(etaourl)
        time.sleep(.2)
        pass_urls.append(etaourl)

        if count >= 10: #没刷完十个连接就保存一下.
            with open("pass.json", 'w') as f:
                json.dump(pass_urls, f, ensure_ascii=False)
        else:
            count += 1

    with open("pass.json", 'w') as f:
        json.dump(pass_urls, f, ensure_ascii=False)


def main(forceUpdate=False):

    users, _isForceUpdateEtaoUrl = [], ''
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

    conf = configparser.ConfigParser()
    conf.read('config.ini')
    _users = conf.get(conf.sections()[0], 'user')
    _isForceUpdateEtaoUrl = conf.get("users", 'isForceUpdateEtaoUrl')

    if _users and _isForceUpdateEtaoUrl:
        users = str(_users).split(",")
        _isForceUpdateEtaoUrl = int(_isForceUpdateEtaoUrl)
        if _isForceUpdateEtaoUrl == 1 or forceUpdate:  # 如果配置文件或程序执行中任何一处要求强制更新url 就更新他
            _isForceUpdateEtaoUrl = 1

    forceUpdate = False if _isForceUpdateEtaoUrl == 0 else True
    names = users

    if not names:
        print(u"读取配置文件出错,退出")
        return

    if names[0] == 'userName1':
        _name = input(u"请输入你的淘宝用户名:")
        if _name:  # 不检查错误
            _names=_name.split(",")
            if isinstance(_names,list):
                names=_names
            else:
                names[0] = _name
                names[1] = ''
    elif names[1] == 'userName2':
        names[1] = ''

    main_urls = ['http://www.zuanke8.com/thread-4470619-1-1.html', ]
    # main_urls = ['http://www.zuanke8.com/thread-4423688-1-1.html', '']

    # names=['dengyangpp','sky0910104475']
    zkbSpider = Spider(main_urls)

    filename = "pintuanurls.json"
    global pinTuanurls
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            pinTuanurls = json.load(f)

    if len(pinTuanurls)<=3 or forceUpdate:
        zkbSpider.getEtaoTargetUrl()

    if os.path.exists("pass.json"):
        with open('pass.json', 'r') as f:
            etaopass = json.load(f)
        for i in etaopass: #去除刷过的连接
            if i in pinTuanurls:
                pinTuanurls.pop(i)

    if len(pinTuanurls) >= 3:
        # max_process = len(names) if not (multiprocessing.cpu_count() > len(
        #     names)) else multiprocessing.cpu_count()
        # print(names,max_process)
        # Ppool = multiprocessing.Pool(max_process)  # 加入多进程并发

        time.sleep(1)
        threads=[]
        for name in names:
            if name:
                t=threading.Thread(target=go_,args=(name,pinTuanurls))
                # Ppool.apply_async(func=go_, args=(name, pinTuanurls))
                print('创建了 {name} 的菜鸟裹裹自动化进程'.format(name=name))
                t.setDaemon(True)
                t.start()
                threads.append(t)
        # Ppool.close()
        # Ppool.join()
        for t in threads:
            t.join()
    else:
        print("一淘链接的数量不够3条.程序退出中...")
        exit(0)
    print("刷完了...")




if __name__ == "__main__":
    print("赚吧ID:make!t   觉得不错请给加个果果吧!亲~~~~")
    main()

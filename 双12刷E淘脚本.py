#!/usr/bin/env python
# encoding: utf-8


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
import threading
import time

import os

import multiprocessing
from selenium import webdriver
import requests
import sys
import configparser
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
sys.path.append(os.path.dirname(__file__))


pinTuanurls = {}


class EtaoGo(object):

    def __init__(self, youName, url=''):
        self.youName = youName
        self.url = url
        self.webclient = webdriver.Chrome()
        self.webclient.implicitly_wait(2)
    def waitElementRady(self,times=0):
        try:
            return self.webclient.find_element_by_class_name("act-btn-single")
        except BaseException:
            time.sleep(0.2)
            if times>=3:#失败3次就放弃
                return False
            self.webclient.get(self.url)
            time.sleep(.8)
            return self.waitElementRady(times+1)



    def shuaIt(self, url,times=0):
        self.url = url
        # self.webclient.execute_script("window.open('" + self.url + "')")
        self.webclient.get(url)
        bt = self.waitElementRady()
        if bt:
            bt.click()
        else:
            print(self.youName+"点击"+self.url+"出错,放弃这个链接!")
            return times

        for i in range(3):
            try:
                input_name = self.webclient.find_element_by_xpath(
                    r'//*[@id="draw-popup"]/div[2]/div[1]/div[2]/div[3]/input')
                input_name.send_keys(self.youName)

                submitBt = self.webclient.find_element_by_xpath(r'//*[@id="draw-popup"]/div[2]/div[1]/div[3]/div/div')
                time.sleep(.1)
                submitBt.click()
                time.sleep(.6)
                break
            except Exception as e:
                print(self.youName+"准备点击"+self.url+"时候出错了.重试中",e)
                time.sleep(.8)

        time.sleep(.3)
        self.webclient.delete_all_cookies()
        if times>=2:#只能爽两次.
            print("浏览器需要关闭!")
            self.webclient.quit()
            self.webclient=webdriver.Chrome()
            return 0
        # return times+1
        # if times>=2:
        #     print("准备切换TAB")
            # self.webclient.execute_script("window.open('data;.')")
            # self.webclient.close()
            # ActionChains(self.webclient).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
            # self.webclient.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
            # self.webclient.execute_script( "window.open('"+self.url+"')")
            # time.sleep(5)
            # ActionChains(self.webclient).key_down(Keys.CONTROL).key_down(Keys.TAB).key_up(Keys.CONTROL).key_up(Keys.TAB).perform()
            # ActionChains(self.webclient).key_down(Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL).perform()
            # return 0
        # self.webclient.close()
  #       self.webclient.execute_script('''  window.opener=null;
  # window.open('','_self');
  # window.close();''')
        return times+1

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
        content = content.replace(" ", "")
        ret = re.search(u'共(\d*)页', content)
        if ret:
            print(ret.group())
            return ret.group(1)

    def _etaotargetUrl(self, content):
        ret = re.findall(
            r'(http://drfhj.*[a-zA-Z0-9]{32,50})" target="',
            content)
        if ret:
            return ret

    def getEtaoTargetUrl(self):
        'http://drfhj.com/my.htm?code=p1j3wKXg48PrWUqRN1AbdpHOMlIAthze'
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


def go_(name,urls):
    etg = EtaoGo(name)
    etg.webclient.implicitly_wait(3)
    count=0
    pass_urls=[]
    # print(name,urls)
    Procetimes=0
    for etaourl in urls.keys():
        print("进程 {name} 准备点击 {url}".format(name=etg.youName,url=etg.url))
        # webClientRunTimes=etg.shuaIt(etaourl,webClientRunTimes+1)
        Procetimes=etg.shuaIt(etaourl,Procetimes+1)
        time.sleep(.3)
        pass_urls.append(etaourl)
        if count>=10:
            with open("pass.json", 'w') as f:
                json.dump(pass_urls, f, ensure_ascii=False)
        else:
            count+=1
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
    conf.read('config.ini',encoding='utf-8')
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

    main_urls=['http://www.zuanke8.com/thread-4535621-1-1.html','http://www.zuanke8.com/thread-4535840-1-1.html']
    main_urls.reverse()
    # main_urls = ['http://www.zuanke8.com/thread-4423688-1-1.html', '']
 
    zkbSpider = Spider(main_urls)

    filename = "pintuanurls.json"
    global pinTuanurls
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            pinTuanurls = json.load(f)

    else:
        zkbSpider.getEtaoTargetUrl()
    if forceUpdate:
        zkbSpider.getEtaoTargetUrl()

    if os.path.exists("pass.json"):
        with open('pass.json', 'r') as f:
            etaopass = json.load(f)
        for i in etaopass:
            if i in pinTuanurls:
                pinTuanurls.pop(i)
    threads=[]
    if len(pinTuanurls) >= 3:
        # max_process=len(names) if not multiprocessing.cpu_count()>len(names) else multiprocessing.cpu_count()
        # Ppool=multiprocessing.Pool(max_process) #加入多进程并发
        # for name in names:
        #     if name:
        #         Ppool.apply_async(func=go_,args=(name,pinTuanurls))
        #         print('创建了处理 {name} 一淘进程'.format(name=name))
        #
        # Ppool.close()
        # Ppool.join()
        for name in names:
            t = threading.Thread(target=go_, args=(name, pinTuanurls))
            # Ppool.apply_async(func=go_, args=(name, pinTuanurls))
            print('创建了处理 {name} 一淘进程'.format(name=name))
            t.setDaemon(True)
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    else:
        print("一淘链接的数量不够3条")

    print("程序执行结束!")

if __name__ == "__main__":
    print("赚吧ID:make!t   觉得不错请给加个果果吧!亲~~~~")
    time.sleep(1.5)
    main()

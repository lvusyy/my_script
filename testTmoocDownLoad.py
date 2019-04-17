#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# author:lvusyy   (https://github.com/lvusyy)    
import time
import requests
import bs4
import os
import copy
import re
import js2py
# import urllib.request
# by:lvusyy
# node : 登录功能未完成,自行替换cookies使用. 选装依赖包. 还需安装 ffmpeg http://ffmpeg.org/
headers = {
    'Origin': 'http://tts.tmooc.cn',
    'Referer': 'http://tts.tmooc.cn/video/showVideo?menuId=627532&version=NSDTN201801',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    'Cookie': 'Hm_lvt_51179c297feac072ee8d3f66a55aa1bd=1552986061,1553327593,1553475897,1554690849; TMOOC-SESSION=E80A40C1E1BD4118AB7ED26827708F2B; sessionid=E80A40C1E1BD4118AB7ED26827708F2B|E_bfum0l4; cloudAuthorityCookie=0; versionListCookie=NSDTN201801; defaultVersionCookie=NSDTN201801; versionAndNamesListCookie=NSDTN201801N22NLinux%25E4%25BA%2591%25E8%25AE%25A1%25E7%25AE%2597%25E5%2585%25A8%25E6%2597%25A5%25E5%2588%25B6%25E8%25AF%25BE%25E7%25A8%258BV06; courseCookie=LINUX; stuClaIdCookie=659729; tedu.local.language=zh-CN; Hm_lpvt_51179c297feac072ee8d3f66a55aa1bd=1554725946; JSESSIONID=A2FC286C2F07FC0289E6C86C703B3644; isCenterCookie=yes; Hm_lvt_e997f0189b675e95bb22e0f8e2b5fa74=1554690867,1554693342,1554693345,1554725950; Hm_lpvt_e997f0189b675e95bb22e0f8e2b5fa74=1554725950'
}
rsp = requests.session()
path = os.path.dirname(os.path.abspath(__file__))



#todo
def getCpass(passwd):
    '返回加密后的密文'
    js='http://cdn.tmooc.cn/tmooc-web/js/jsmd5.js'
    'download js file'
    _rsp=rsp.get(js,headers=headers)
    if _rsp.status_code!=200:
        print('下载js失败！')
        return -1
    with open ('jsmd5.js','wb') as f:
        f.write(_rsp.content)


    #TODO
    ### 追加js语句到js文件。让js执行的时候自动输出加密后的密文
    os.system('echo " return MD5('+passwd +');" >> jsmd5.js')
    jsTextdata=open('jsmd5.js','rb',encoding='utf8').read()
    jsdata=js2py.eval_js(jsTextdata)
    if jsdata:
        return jsdata
    return ''#fail

def merge(file):
    '合并mp4文件'
    # 获取当前文件夹内有没有index.m3u8
    amorpm=file.replace('.m3u8','')[-2::]
    if os.path.exists(file):
        filecontent = ''
        f = open(file, "r")
        if f.read().find("http")!=-1:
            f.seek(0,0)
            # f = open(file, "r")
            for i in f.readlines():
                if i.find("http") != -1:
                    if i.find(".key") != -1:
                        filecontent += '#EXT-X-KEY:METHOD=AES-128,URI="'
                    # filecontent += amorpm+i.split('/')[-1].replace("-", '')
                    filecontent +=i.split('/')[-1].replace("-", '')

                else:
                    filecontent += i

            with open(file, "w") as f:
                f.write(filecontent)
            print(file + "处理完成")

    dir_ = os.path.dirname(file)
    filename = file.split("/")[-1]

    if os.path.exists(os.path.join(dir_, file.split('/')[-2]) +amorpm+ ".mp4"):
        #mp4文件已经合成过了.
        return
    cmd = "cd " + dir_ + '; ffmpeg -allowed_extensions ALL -protocol_whitelist "file" -i ' + filename + ' -c copy video.mp4'
    os.system(cmd)
    print(file + " 处理完成!")
    try:
        os.rename(os.path.join(dir_, "video.mp4"), os.path.join(dir_, file.split('/')[-2]) +amorpm+  ".mp4")
        #合并成功后,删除源分片的文件.防止和下次文件冲突,,,,,,,ps 实际并不会冲突,因为文件名不是一样的
        os.system("rm -f "+dir_+"/*.ts")
        ##### 注意这里．合成完毕后需要删除key或重新命名文件. 但是static.key冲突. 而且改名会出错.原因未知?
        os.remove(os.path.join(dir_, "static.key"))
    except Exception :
        print("执行合并视屏文件出错!!!")


def downloadALLTs(ref, heads, path, tscontent):
    ''
    # 解析下载文件链接

    filecontent=''
    if hasattr(tscontent,'text'):
        filecontent=tscontent.text

    reresp = re.findall(r'(http.*)', filecontent)
    heads['Referer'] = ref
    # heads['Cookie']=''
    for i in reresp:
        if len(i) > 5:
            filename = str(i.replace('"', "")).split("/")[-1].replace('-', '')
            # amorpm=i.split('/')[-2][-2:]
            # if filename.find('static.key')!=-1 and filename.find('am') ==-1 and filename.find('pm')==-1:
            #     filename=amorpm+filename
            #防止key 文件冲突,所以每次需要下载分片数据的时候默认就更新key文件
            if os.path.exists(os.path.join(path, filename)) and filename.find('static.key')==-1:
                continue
            ret=rsp.get(i.replace('"',""),headers=heads)
            content=ret.content
            # request = urllib.request.Request(i.replace('"', ""), headers=heads)
            # response = urllib.request.urlopen(request)
            # content = response.read()
            with open(os.path.join(path, filename), "wb") as f:
                f.write(content)
            time.sleep(0.05)

    print("单个视频的所需分片资源下载完成!")

def getPPT(ref,path,url):
    '下载ppt'
    hd = copy.deepcopy(headers)
    hd.pop('Referer')
    # 如果ppt.html文件存在就不下载了.跳过
    if os.path.exists(os.path.join(path, 'ppt.html')) or not url:
        return
    rst = rsp.get(url, headers=hd)
    if rst.status_code != 200:
        print(url, "ppt.html页面下载失败!")
        return
    with open(os.path.join(path, "ppt.html"), "wb") as f:
        f.write(rst.content)

    bsrst = bs4.BeautifulSoup(rst.text)
    imgs = bsrst.find_all("img")
    baseurl = url.replace('ppt.html', '')
    for i in imgs:
        try:
            imgrst = rsp.get(baseurl + i['src'], headers=hd)
            if imgrst.status_code != 200:
                raise IOError
            imgpath = i['src'].replace(i['src'].split('/')[-1], '')
            if not os.path.exists(os.path.join(path, imgpath)):
                os.mkdir(os.path.join(path, imgpath))
            with open(os.path.join(path, i['src']), 'wb') as    f:
                f.write(imgrst.content)

        except Exception:
            print("下载ppt.html图片时候出错")

    print(baseurl,"PPT页面下载完成!")

def getExercise(ref,path,url):
    '下载作业页面'
    hd = copy.deepcopy(headers)
    hd.pop('Referer')
    #如果index_answer.html文件存在就不下载了.跳过
    if  os.path.exists(os.path.join(path, 'index_answer.html')) or not url:
        return
    url=str(url).replace('.html','')+"_answer.html"
    rst = rsp.get(url, headers=hd)
    if rst.status_code != 200:
        print(url, "作业页面下载失败!")
        return
    with open(os.path.join(path, "index_answer.html"), "wb") as f:
        f.write(rst.content)
    print("作业页面下载完成!")

def getCase(ref, path, url):
    '下载案例页面的数据和图片'
    hd = copy.deepcopy(headers)
    hd.pop('Referer')
    #如果index.html文件存在就不下载了.跳过
    if  os.path.exists(os.path.join(path, 'index.html')) or not url:
        return
    rst = rsp.get(url, headers=hd)
    if rst.status_code != 200:
        print(url, "案例页面下载失败!")
        return
    with open(os.path.join(path, "index.html"), "wb") as f:
        f.write(rst.content)

    bsrst = bs4.BeautifulSoup(rst.text)
    imgs = bsrst.find_all("img")
    baseurl = url.replace('index.html', '')
    for i in imgs:
        try:
            imgrst = rsp.get(baseurl + i['src'], headers=hd)
            if imgrst.status_code != 200:
                raise IOError
            imgpath = i['src'].replace(i['src'].split('/')[-1], '')
            if not os.path.exists(os.path.join(path, imgpath)):
                os.mkdir(os.path.join(path, imgpath))
            with open(os.path.join(path, i['src']), 'wb') as    f:
                f.write(imgrst.content)
            #jquery css
            urls=['index.files/jquery.min.js','index.files/jquery.snippet.js',
                  'index.files/main.js','index.files/index.css','index.files/jquery.snippet.css']

            for urljscss in urls:
                content=rsp.get(os.path.join(baseurl,urljscss),headers=hd)
                if imgrst.status_code != 200:
                    raise IOError

                with open(os.path.join(path, urljscss), 'wb') as    f:
                    f.write(content.content)

        except Exception:
            print("下载图片时候出错")

    print("案例页面下载完成!")

def getvideos(ref, path, url):
    '获取视屏页的视屏信息'
    videoUrls = []
    hd=copy.deepcopy(headers)
    hd['Referer'] = 'http://www.tmooc.cn/'
    stra = 'http://videotts.it211.com.cn/'
    mRSP = rsp.get(url, headers=hd)
    bs = bs4.BeautifulSoup(mRSP.text)
    bs = bs.find_all('div', class_='video-list')

    for i in bs:
        p = i.find_all('p')
        for s_p in p :
            mid=s_p.get('id',False)

            if not mid:
                print(url + " 下载失败")
                return

            mid = mid.replace('active_', '')
            mid = mid.replace('.m3u8', '')

            strfull = stra + mid + '/' + mid + '.m3u8'
            videoUrls.append(strfull)

            downloadts(url, path, strfull)
    if len(videoUrls) < 1:
        print("该页面可能没有视屏,或者登录已经失效!")


def downloadts(ref, path, url):
    '下载m3u8文件'

    #文件已经存在就不要在保存了
    filename = url.split("/")[-1]
    if not os.path.exists(os.path.join(path, filename)):
        myheaders = copy.deepcopy(headers)
        myheaders['Origin'] = 'http://tts.tmooc.cn'
        myheaders['Referer'] = ref
        rspcontent = rsp.get(url, headers=myheaders)

        if rspcontent.status_code != 200:
            print("准备m3u8页面出错")
            return
        with open(os.path.join(path, filename), "wb") as f:
            f.write(rspcontent.content)
    else:
        #如果不是从网络获取的就从本地获取
        with open(os.path.join(path, filename), "rb") as f:
            rspcontent=f.read()

    downloadALLTs(ref, headers, path, rspcontent)

    merge(os.path.join(path, filename))


def downloadOnePage(allurldata):
    '解析需要的视屏页和文档页信息'
    # [{title:"xxx",allurldata:http://xxx},{xxxx}]
    videoCount = 0
    for i in allurldata:
        videoCount += 1
        mpath = os.path.join(path, str(videoCount) +"_"+ i.get("title", ""))
        # mpath = os.path.join(path, str(videoCount) + i.get("title", ""))
        if not os.path.exists(mpath):
            os.mkdir(mpath)
        if videoCount>=83:
            getCase('', mpath, i.get('casePageurl'))
            getPPT('',mpath,i.get('PPT'))
            getvideos('', mpath, i.get('videoPageurl')) #jump this
            getExercise('',mpath,i.get('ZY'))


def main():
    headers['Referer'] = 'http://www.tmooc.cn/'
    mrsp = rsp.get("http://tts.tmooc.cn/studentCenter/toMyttsPage", headers=headers)
    if mrsp.status_code != 200:
        print("失败!", mrsp.status_code)
        exit(1)
    # print(rsp.text)

    bs = bs4.BeautifulSoup(mrsp.text, 'html.parser')
    # getalldata

    data = []
    # 获取有效区域
    # bs1=bs.find_all("div",class_="container")
    # bs1[0].select("")
    # bs.find_next()
    bs = bs.find_all('li', class_="opened")

    if len(bs) < 1:
        print("没打开网页,或者登录已经失效了!")

        return

    for i in bs:
        tempdata = {}
        tempdata['title'] = i.find("p").string.replace('\t', '').replace('\r\n', '').replace(' ', '').replace('-',
                                                                                                              '_').replace(
            ',', '_')
        tempdata['title'] = tempdata['title'].replace('：', '').replace('、', '_').replace('/', '')

        for url in i.select("li>a"):
            if url.text == "视频":
                # is target
                # print(url['href'])
                tempdata['videoPageurl'] = url['href']
            elif url.text == "案例":
                tempdata['casePageurl'] = url['href']
            elif url.text == "PPT":
                tempdata['PPT'] = url['href']
            elif url.text == "作业":
                tempdata['ZY'] = url['href']

        data.append(tempdata)

    if len(data) > 10:
        print("解析视频下载页面完成,共{count}个记录".format(count=len(data)))

        downloadOnePage(data)


if __name__ == "__main__":
    main()

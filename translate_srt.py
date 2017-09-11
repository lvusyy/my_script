#!coding=utf-8


##
#利用Google Api 翻译字幕
# [翻译目录下所有的.srt文件 逐句翻译]
# [使用场景 用youtube-dl 下载lynda的课程 带字幕  youtube-dl --write-sub --cookies 你的cookies 你要下载的可能页面]
# [下载完成之后运行此脚本. 脚本就会逐句翻译并且保留原有的英文字母.]
#[##注意 其中cdown的srt模块 不支持下载下来的字幕格式,我修改了下. srt.py 下载到脚本目录即可]
# by:lvusyy
#
# https://github.com/ssut/py-googletrans
# https://github.com/cdown/srt

import functools
import os
from time import sleep

from googletrans import Translator
import srt



class subtitle(object):
    '''字幕相关类 待补充'''
    def __init__(self,filenName=None):
        self.str_srt_file=filenName
        self.str_srt_file_conten=''
        self.list_srt_parse=[]
        self.int_srt_next_id=-1
    
        if self.str_srt_file:
            self.parse_srt_file()

    def parse_srt_file(self,fileName=None):
        if not fileName and  self.str_srt_file and os.path.exists(self.str_srt_file):
            # srtcontent=self.getSrt_from_file(self.str_srt_file)
            # srtparse=srt.parse(srtcontent)
            # self.list_srt_parse = list(srtparse)
            self.list_srt_parse=list(srt.parse(self.getSrt_from_file(self.str_srt_file)))

        else:
            print("Error: --> 请指定字幕文件\n")
            exit(0)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.list_srt_parse)-1 > self.int_srt_next_id:
            self.int_srt_next_id += 1
            return self
        else:
            raise StopIteration("is ending...")

    def getCurrentWord(self):
        if self.int_srt_next_id<len(self.list_srt_parse):
           return self.list_srt_parse[self.int_srt_next_id].content
        return ''

    def __str__(self):
        return self.getCurrentWord()

    def join_translatedtext_to_srt(self,value,isdoubel=True,isfontsmall=True,isToOneLine=True):
        fonts=''
        oldcontent=''
        if isfontsmall:                               #设置小字体
            fonts='{\\fn黑体\\fs10}'
        if isdoubel:                                  #双字幕
            oldcontent=self.list_srt_parse[self.int_srt_next_id].content
        if isToOneLine:                               #转换为一行
            oldcontent=oldcontent.replace('\r\n',' ').replace('\n',' ')
            value=value.replace('\r\n',' ').replace('\n',' ')



        self.list_srt_parse[self.int_srt_next_id].content=fonts+oldcontent+'\n'+value+'\n'

    def getSrt_from_file(self, fileName, coding='utf-8'):
        with open(file=fileName,mode="r",encoding=coding) as f:
            self.str_srt_file_conten=f.read()
        return self.str_srt_file_conten

    def saveSrt_to_file(self,fileName=None):
        try:
            if fileName is None:
                fileName=self.str_srt_file
            fileName=fileName[:-4]+'.zh_CN'+fileName[-4:]
            fileName=str(fileName).replace('en','')
            with open(file=fileName, mode='wb+') as f:
                f.write(srt.compose(self.list_srt_parse).encode('utf-8'))
        except Exception as e :
            print('保存到字幕时候出错了',e)

class translate(object):
    '''翻译'''
    def __init__(self):
        self.trs=Translator()
        sleep(500/1000)

    def trans_Text(self,text,dest_language="zh-CN"):
        try:
            if self.trs.detect(text).lang==dest_language:
                return text
            return self.trs.translate(text,dest=dest_language).text
        except NameError:
            print('翻译时候发生错误.本段落不翻译',text)
            return text
        except ConnectionError:
            print('翻译时候遇到网络问题..',text)


def trans_a_Srt_file(filename):
    srt_subtitle=subtitle(filename)
    trans=translate()
    for i in srt_subtitle:
        print(i)
        srt_subtitle.join_translatedtext_to_srt(trans.trans_Text(i.getCurrentWord()))
        sleep(10/1000)

    print('翻译完成.写入str中.',filename)
    srt_subtitle.saveSrt_to_file()

def trans_all_srt_file(dirs='.'):
    for file in  os.listdir(dirs):
        if not os.path.isdir(file):
            print('file is',file)
            if file[-4:].upper()==".SRT" and file.upper().find("CN")==-1 and file.upper().find("ZH")==-1 :
                print('命中srt文件...',os.path.join(dirs,file))
                trans_a_Srt_file(os.path.join(dirs,file))
                os.rename(os.path.join(dirs,file),os.path.join(dirs,file)+".bak")
        else:
            print('in dir')
            return trans_all_srt_file(os.path.join(dirs,file))

    print('all done')

if __name__ == '__main__':
    trans_all_srt_file(r'C:\Users\Administrator\Desktop\temp\go_lynda') #设置你字幕所在的目录. 默认会遍历所有子目录

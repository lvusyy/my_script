#!coding=utf-8


##
#利用Google Api 翻译字幕
#
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
            self.list_srt_parse=list(srt.parse(self.getSrt_form_file(self.str_srt_file)))

        else:
            print(u"Error: --> 请指定字幕文件\n")
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
            fonts=u'{\\fn黑体\\fs10}'
        if isdoubel:                                  #双字幕
            oldcontent=self.list_srt_parse[self.int_srt_next_id].content
        if isToOneLine:                               #转换为一行
            oldcontent=oldcontent.replace(u'\r\n',u' ').replace(u'\n',u' ')
            value=value.replace(u'\r\n',u' ').replace(u'\n',u' ')



        self.list_srt_parse[self.int_srt_next_id].content=fonts+oldcontent+u'\n'+value+u'\n'

    def getSrt_form_file(self,fileName,coding='utf-8'):
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
            print(u'保存到字幕时候出错了',e)

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
            print(u'翻译时候发生错误.本段落不翻译',text)
            return text
        except ConnectionError:
            print(u'翻译时候遇到网络问题..',text)


def trans_a_Srt_file(filename):
    srt_subtitle=subtitle(filename)
    trans=translate()
    for i in srt_subtitle:
        print(i)
        srt_subtitle.join_translatedtext_to_srt(trans.trans_Text(i.getCurrentWord()))
        sleep(10/1000)

    print(u'翻译完成.写入str中.',filename)
    srt_subtitle.saveSrt_to_file()

def trans_all_srt_file(dir='.'):
    for file in  os.listdir(dir):
        if not os.path.isdir(file) :
            if file[-4:].upper()==".SRT":
                print(u'命中srt文件...',os.path.join(dir,file))
                trans_a_Srt_file(os.path.join(dir,file))
        else:
            return trans_all_srt_file(os.path.join(dir,file))

    print(u'所有文件处理完毕...')

if __name__ == '__main__':
    trans_all_srt_file(u'E:\lynda\Learning_Python')

#!coding:utf-8
# by:lvusyy
# orangePi 使用 nokia 5110 显示屏 展示运行状态

import commands
import os
import time

SLEEPTIME=10 #every 10s

times=0
WANIP=commands.getstatusoutput("curl -s http://members.3322.org/dyndns/getip")[1]
def getdatas():
    line0='UpTime:{}'
    line1='TP:{}.PC:{}'
    line2='LD:{}'
    line3='Frpc:{}'#running stop
    line4='WANIP:'
    line5='Net:{}'
    uptime= commands.getstatusoutput("uptime|awk '{print $3$4}'")[1][0:-1]
    temp= commands.getstatusoutput("cat /sys/class/thermal/thermal_zone0/temp")[1]
    psCount= commands.getstatusoutput("ps aux|wc -l")[1].replace(' ','')
    load =  commands.getstatusoutput("uptime|awk -Faverage: '{print $2}'")[1].replace(' ','')
    global times
    if times>=60:
        wanip=commands.getstatusoutput("curl -s http://members.3322.org/dyndns/getip")[1]
        global WANIP
        WANIP=wanip
        times=0
    else:
        wanip=WANIP
        times += 1
    network= commands.getstatusoutput("ping baidu.com -c 1 2>/dev/null|grep -q time && echo Online ||echo *offline*")[1]
    if network.find('offline')!=-1:
        times=60
    frpc= commands.getstatusoutput("ps aux|grep -q frpc && echo Running ||echo Stoped")[1]

    return [line0.format(uptime),line1.format(temp,psCount),line2.format(load),line3.format(frpc),line5.format(network),wanip if wanip else "**Offline**"]
def show():
    ''
    os.system('./nokia r')
    line=0
    a=['a','b','3','d','e','6']
    for i in getdatas():

        # print("nokia {} {}".format(line,i))
        os.system("./nokia +{} {}".format(a[line],i))
        line += 1
    os.system('./nokia c 60')
    os.system('./nokia s')


def loop():
    ''
    while True:
        time.sleep(SLEEPTIME)
        show()

def main():
    loop()


if __name__=="__main__":
    main()

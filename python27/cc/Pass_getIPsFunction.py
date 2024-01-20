#coding=utf-8 测试通过：获取代理网站的代理IP列表 2017-1-23
#             将header模仿浏览器登录
#             多个代理站点因为BeautifulSoup(html_doc,'lxml')不能统一，暂时只能用一个站点
from bs4 import BeautifulSoup
from time import ctime,sleep
import urllib2, requests,datetime,threading,thread,os
from lib import deflibs
class GetIPList:
    ips=[];idx =[0]
    def getips(self):
        arr_urls = deflibs.UrlsFromTxt('ProxySiteList.txt')
        for _url2 in arr_urls:
            try:
                html_doc = deflibs.Urlopen(_url2)
            except:
                sleep(2)
                continue
            print _url2;sleep(0.7)
            deflibs.SoupFindIp(html_doc, self.idx, self.ips)
            deflibs.GetProxyIpFromTag(html_doc, self.idx, self.ips)
        return self.ips
if __name__ == '__main__':
    Ins_getIP = GetIPList()
    Ins_getIP.getips()
    for a, val in enumerate(Ins_getIP.ips):
        print str(a) + ":" +val
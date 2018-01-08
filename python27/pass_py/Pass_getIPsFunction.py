#coding=utf-8 测试通过：获取代理网站的代理IP列表 2017-12-26
from bs4 import BeautifulSoup
from time import ctime,sleep
import urllib2, requests,datetime,threading,thread
class GetIPList:
    ips=[]
    __idex =1
    PageCount = 2
    urlstr = 'http://www.kuaidaili.com/free/intr/'
    def __init__(self, url="",pageCount = 1):
        if  url!="" :
            self.urlstr = url
        if  pageCount>1 :
            self.PageCount = pageCount
    def EachHtmlPage(self):
        for page in range(1, self.PageCount):
            html_doc = urllib2.urlopen(self.urlstr + str(page)).read()
            soup = BeautifulSoup(html_doc,'lxml')
            trs = soup.find('table').find_all('tr')
            sleep(1)
            for tr in trs[1:]:
                tds = tr.find_all('td')
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                protocol = tds[3].text.strip()
                if protocol == 'HTTP' or protocol == 'HTTPS':
                    print '%s. %s=%s:%s' % (self.__idex,protocol, ip, port)
                    self.ips.append(ip + ':' + port)
                    self.__idex = self.__idex + 1

if __name__ == '__main__':
    Ins_getIP = GetIPList()
    Ins_getIP.PageCount = 3
    Ins_getIP.EachHtmlPage()
    # print Ins_getIP.ips
    # print Ins_getIP.urlstr
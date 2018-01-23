#coding=utf-8 测试通过：获取代理网站的代理IP列表 2017-1-23
#             将header模仿浏览器登录
#             多个代理站点因为BeautifulSoup(html_doc,'lxml')不能统一，暂时只能用一个站点
from bs4 import BeautifulSoup
from time import ctime,sleep
import urllib2, requests,datetime,threading,thread,os
class GetIPList:
    ips=[]
    __idex =1
    arr_ProxySite = []
    def __init__(self):
       pass
    def EachHtmlPage(self,urlstr):
        if urlstr[0] == '#':
            return
        _url = urlstr.split(',')[1]
        _pageCount = int(urlstr.split(',')[0])
        print _url + ' start :'
        for page in range(1, _pageCount+1):
            _url2 = _url + str(page)
            if _pageCount==1 :
                _url2 = _url
            headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
            req = urllib2.Request(_url2,headers=headers)
            html_doc = urllib2.urlopen(req).read()
            soup = BeautifulSoup(html_doc,'lxml')
            trs = soup.find('table').find_all('tr')
            sleep(0.7)
            for tr in trs[1:]:
                tds = tr.find_all('td')
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                protocol = tds[3].text.strip()
                if protocol == 'HTTP' or protocol == 'HTTPS':
                    print '%s. %s=%s:%s' % (self.__idex,protocol, ip, port)
                    self.ips.append(ip + ':' + port)
                    self.__idex = self.__idex + 1
    def ReadProxySiteList(self):
        ProxySiteList = os.path.abspath('ProxySiteList.txt')
        if not os.path.exists(ProxySiteList):
            print '[ ProxySiteList.txt ] not exist !'
            exit()
        file = open(ProxySiteList)
        for line in file:
            self.arr_ProxySite.append(line.replace("\n", ""))
    def ForeachProxySiteList(self):
        self.ReadProxySiteList()
        for url in self.arr_ProxySite:
            self.EachHtmlPage(url)


if __name__ == '__main__':
    Ins_getIP = GetIPList()
    Ins_getIP.ForeachProxySiteList()
    # print Ins_getIP.ips
    # print Ins_getIP.urlstr
#coding=utf-8 测试通过：获取代理网站的代理IP列表 2017-12-26
from bs4 import BeautifulSoup
from time import ctime,sleep
import urllib2, requests,datetime,threading,thread
import pass_py.Pass_getIPsFunction
import telnetlib

# Ins_getIP = pass_py.Pass_getIPsFunction.GetIPList()
# Ins_getIP.PageCount = 10
# Ins_getIP.EachHtmlPage()
# arr_ip = Ins_getIP.ips
# fileObject = open("ip.txt", 'w')
# for ip in arr_ip:
#     fileObject.write(ip)
#     fileObject.write('\n')
# fileObject.close()

arr_ip=[]
file = open("ip.txt")
for line in file:
    arr_ip.append(line.replace("\n", ""))


class thd:
    threads=[]
    __arr=['a','b']

    def __init__(self,ListIp = []):
        if ListIp :
            self.__arr = ListIp
    def ckid(self,ip,idx):
        try:
            # starttime = datetime.datetime.now()
            r = requests.get('http://www.baidu.com/', proxies={"http": 'http://' + ip})
            print r.text
            # endtime = datetime.datetime.now()
            # timecha = (endtime - starttime).seconds
        except:
            pass # str(idx) + ". "+ ip + " ok"
        else:
            print  '%s:%s 成功'%(str(idx),ip)
    def ForAdd(self):
        idx = 1
        for item in self.__arr:
            t1 = threading.Thread(target=self.ckid, args=(item,idx,))
            self.threads.append(t1)
            idx = idx +1
    def ForDo(self):
        if self.threads.count > 0:
            for aa in self.threads:
                aa.setDaemon(True)
                aa.start()
            aa.join()

    def TelnetCheck(self,ip,idx):
        arrIP = ip.split(":")
        try:
            telnetlib.Telnet(arrIP[0], port=arrIP[1], timeout=20)
        except:
            pass #print 'connect failed'
        else:
            print ip + ' success'
if __name__ == '__main__':
    td = thd(arr_ip)
    td.ForAdd()
    td.ForDo()



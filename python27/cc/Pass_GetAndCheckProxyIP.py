#coding=utf-8 测试通过：1 调取其他py文件里的函数方法，获取代理的IP列表，写入txt文件  2018-1-23 修改
#                       2 多线程验证代理ip的可用性，
import urllib2, requests,threading
import Pass_getIPsFunction
import telnetlib,os
if not os.path.exists('../temp'):
    os.makedirs('../temp')
txtfile=os.path.abspath('../temp/ip.txt')
txtfile_valid=os.path.abspath('../temp/ip_valid.txt')
if not os.path.exists(txtfile):
    Ins_getIP = Pass_getIPsFunction.GetIPList() # 在配置文件ProxySiteList.txt中定义url和页码数
    Ins_getIP.getips()
    arr_ip = Ins_getIP.ips
    fileObject = open(txtfile, 'w')
    for id, ip in enumerate(arr_ip):
        fileObject.write(ip)
        fileObject.write('\n')
        print str(id)+" : "+ip
    fileObject.close()

arr_ip=[]
arr_ip_valid=[]
file = open(txtfile)
for line in file:
    arr_ip.append(line.replace("\n", ""))


class thd:
    threads=[]
    __arr=['a','b']

    def __init__(self,ListIp = []):
        if ListIp :
            self.__arr = ListIp
    def CC(self,ip,idx):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        req = urllib2.Request(_url2, headers=headers)
        html_doc = urllib2.urlopen(req).read()
    def ckid(self,ip,idx):
        try:
            # starttime = datetime.datetime.now()
            r = requests.get('http://www.winshang.com/zt/51list.aspx', proxies={"http": 'http://' + ip})
            # print r.text
            # endtime = datetime.datetime.now()
            # timecha = (endtime - starttime).seconds
        except:
            pass # str(idx) + ". "+ ip + " ok"
        else:
            print  '%s:%s 成功'%(str(idx),ip)
            arr_ip_valid.append(ip)
    def ForAdd(self):
        idx = 1
        for item in self.__arr:
            t1 = threading.Thread(target=self.TelnetCheck, args=(item,idx,))
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
            arr_ip_valid.append(ip)
    def WriteValiedIpToTxt(self):
        # if os._exists(txtfile_valid):
        #     os.remove(txtfile_valid)
        fileObject = open(txtfile_valid, 'w')
        for ip in arr_ip_valid:
            fileObject.write(ip)
            fileObject.write('\n')
        fileObject.close()
if __name__ == '__main__':
    td = thd(arr_ip)
    td.ForAdd()
    td.ForDo()
    td.WriteValiedIpToTxt()



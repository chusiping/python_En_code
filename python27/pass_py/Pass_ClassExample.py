#coding=utf-8 测试通过：创建类的实例-1.构造函数 2.局部变量调用 3.可变参数 4.定义函数 2017-12-26
import threading
from time import ctime,sleep

class thd:
    threads=[]
    __arr=['a','b']

    def __init__(self,ListIp = []):
        if ListIp :
            self.__arr = ListIp
    def ckid(self,ip):
        print ip
        sleep(2)

    def ForAdd(self):
        for item in self.__arr:
            t1 = threading.Thread(target=self.ckid, args=(item,))
            self.threads.append(t1)
    def ForDo(self):
        if self.threads.count > 0:
            for aa in self.threads:
                aa.setDaemon(True)
                aa.start()

            aa.join()

if __name__ == '__main__':
    arr = []
    td = thd()
    td.ForAdd()
    td.ForDo()



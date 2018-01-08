#coding=utf-8 通过测试：MSSQL数据库操作通用类 2017-12-26
import pyodbc
import time


class ODBC_MS:
    ''''' 对pyodbc库的操作进行简单封装
    pyodbc库的下载地址:http://code.google.com/p/pyodbc/downloads/list
    使用该库时，需要在Sql Server Configuration Manager里面将TCP/IP协议开启
    此类完成对数据库DB的连接/查询/执行操作
    正确的连接方式如下:
    cnxn = pyodbc.connect('DRIVER={SQL SERVER};SERVER=ZHANGHUAMIN\MSSQLSERVER_ZHM;DATABASE=AdventureWorks2008;UID=sa;PWD=wa1234')
    cnxn = pyodbc.connect(DRIVER='{SQL SERVER}',SERVER=r'ZHANGHUAMIN\MSSQLSERVER_ZHM',DATABASE='AdventureWorks2008',UID='sa',PWD='wa1234',charset="utf-8")
    '''

    def __init__(self, DRIVER,SERVER, DATABASE, UID, PWD):
        ''''' initialization '''

        self.DRIVER = DRIVER
        self.SERVER = SERVER
        self.DATABASE = DATABASE
        self.UID = UID
        self.PWD = PWD

    def __init__(self):
        self.DRIVER = '{SQL SERVER}'
        self.SERVER = '.'
        self.DATABASE = 'JH_HousePro'
        self.UID = 'sa'
        self.PWD = '123'
    def __GetConnect(self):
        ''''' Connect to the DB '''

        if not self.DATABASE:
            raise(NameError,"no setting db info")

        self.conn = pyodbc.connect(DRIVER=self.DRIVER, SERVER=self.SERVER, DATABASE=self.DATABASE, UID=self.UID, PWD=self.PWD, charset="UTF-8")
        #self.conn = pyodbc.connect(DRIVER=self.DRIVER, SERVER=self.SERVER, DATABASE=self.DATABASE, UID=self.UID, PWD=self.PWD)
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"connected failed!")
        else:
            return cur

    def ExecQuery(self, sql):
        ''''' Perform one Sql statement '''

        cur = self.__GetConnect() #建立链接并创建数据库操作指针
        cur.execute(sql)#通过指针来执行sql指令
        ret = cur.fetchall()#通过指针来获取sql指令响应数据
        cur.close()#游标指标关闭
        self.conn.close()#关闭数据库连接

        return ret


    def ExecNoQuery(self,sql):
        ''''' Person one Sql statement like write data, or create table, database and so on'''

        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()#连接句柄来提交
        cur.close()
        self.conn.close()



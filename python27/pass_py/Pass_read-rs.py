#coding=utf-8  测试通过：读取数据，插入数据 2017-12-26
import  Pass_py_sqlhelper
ms = Pass_py_sqlhelper.ODBC_MS()

def seleTest():
    # sql = 'select top 3 LoginUnitName from t_LoginUnit'
    sql = '''SELECT   a.name, b.rows
        FROM      sysobjects AS a INNER JOIN  sysindexes AS b ON a.id = b.id
        WHERE   (a.type = 'u') AND (b.indid IN (0, 1))
        AND b.rows > 0  ORDER BY b.rows DESC'''
    rs = ms.ExecQuery(sql)
    for r in rs:
        print r[0] +  ":" + str(r[1])
def InsertTest():
    sql = "INSERT INTO dbo.T_SystemLog(LogType) VALUES('我们在')"
    rt = ms.ExecNoQuery(sql)
    print(rt)


InsertTest()
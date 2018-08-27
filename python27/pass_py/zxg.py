#coding=utf-8 测试通过：访问jrj.com网站接口，得到连续上涨的股票代码
import  requests
import re
import os
# import pyperclip
######## 定义接口
url_1 = 'http://news.mapked.com/api_stock.php?fcname=get_stock'
url_2 = 'http://news.mapked.com/api_stock.php?fcname=get_bk&type=python'
url_3 = 'http://news.mapked.com/api_stock.php?fcname=get_topzxg'
r = requests.get(url_1)
r2 = requests.get(url_2)
r3 = requests.get(url_3)
######## 正则过滤
pattern  = re.compile(r'\d{6}')
r = pattern.findall(r.text)
r = list(set(r)) #去重
r2 = pattern.findall(r2.text)
r3 = pattern.findall(r3.text)
######## 定义blk文件
lxsz_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\ZXG_882f6b072c.blk"
BKG_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\BKG.blk"
DXG_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\DXG.blk"
######## 循环写入
fileObject = open(lxsz_blk, 'w')
for id, code in enumerate(r):
    code = code.replace('"','')
    qianz = "0"
    if code[0] == "6":
        qianz = "1"
    code = qianz + code
    fileObject.write(code)
    fileObject.write('\n')
    print str(id)+" : "+code
fileObject.close()
print u'自选股-股票加入操作完成'
######## 读取dxg.blk 的股票代码，形成一行串
fileObject = open(BKG_blk, 'w')
for id, code in enumerate(r2):
    code = code.replace('"','')
    qianz = "0"
    if code[0] == "6":
        qianz = "1"
    code = qianz + code
    fileObject.write(code)
    fileObject.write('\n')
    print str(id)+" : "+code
fileObject.close()
print u'板块股-股票加入操作完成'
########置顶股
fileObject = open(DXG_blk, 'w')
for id, code in enumerate(r3):
    code = code.replace('"','')
    qianz = "0"
    if code[0] == "6":
        qianz = "1"
    code = qianz + code
    fileObject.write(code)
    fileObject.write('\n')
    print str(id)+" : "+code
fileObject.close()
print u'短线置顶股-股票加入操作完成'
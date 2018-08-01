#coding=utf-8 测试通过：访问jrj.com网站接口，得到连续上涨的股票代码
import  requests
import re
import os
# import pyperclip
######## 定义接口
url_1 = 'http://news.mapked.com/api_stock.php?fcname=get_stock'
r = requests.get(url_1)
######## 正则过滤
pattern  = re.compile(r'\d{6}')
r = pattern.findall(r.text)
r = list(set(r)) #去重

######## 定义blk文件
lxsz_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\ZXG_882f6b072c.blk"
dxg_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\DXG.blk"
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
print u'zxg股票加入操作完成'
######## 读取dxg.blk 的股票代码，形成一行串


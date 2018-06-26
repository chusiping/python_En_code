#coding=utf-8 测试通过：访问jrj.com网站接口，得到连续上涨的股票代码
import  requests
import re
import os
# import pyperclip
######## 定义接口
url_1 = 'http://hqquery.jrj.com.cn/hqstat.do?sort=pl&page=1&size=30&order=desc&disps=d1,d2,d3,d4,d5&disattrs=pl,tr,sl&sortp=d5&_dc=1528770858381'
url_2 = 'http://hqquery.jrj.com.cn/alxzd.do?sort=day&page=1&size=30&order=desc&isup=1&_dc=1528770858382'
url_3 = 'http://hqquery.jrj.com.cn/upindex.do?sort=pl&page=1&size=30&order=desc&_dc=1530019016934'
r = requests.get(url_1)
r2 = requests.get(url_2)
r3 = requests.get(url_3)
######## 正则过滤
pattern  = re.compile(r'("\d{6}")')
r = pattern.findall(r.text+r2.text+r3.text)
r = list(set(r)) #去重

######## 定义blk文件
lxsz_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\ZXG_882f6b072c.blk"
dxg_blk = "D:\\" + u"中国银河证券海王星2017" + "\\T0002\\blocknew\\DXG.blk"
######## 读取lxsz.blk原有的数据
# file = open(lxsz_blk)
# for id, line in enumerate(file):
#     line = line.replace("\n", "")
#     line = '"'+line[1:7]+'"'
#     if line not in r:   # 检查旧的代码和接口里的是否重复
#         print str(id) + " : " + line
#         r.append(line)
# file.close()

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
print u'连续上涨股票加入操作完成'
######## 读取dxg.blk 的股票代码，形成一行串
file = open(dxg_blk)
codes = ""
for id, line in enumerate(file):
    line = line.replace("\n", "")
    if(line==""):
        continue
    line = ''+line[1:7]+'' #去掉双引号还有空字符串
    codes = codes+line+","
    print str(id) + " : " + line
file.close()
######## 创建记事本，把子串放到里面

txtfile = "C:\\Users\\Administrator\\Desktop\\dxg.txt"
file = open(txtfile,"w")
codes = codes.rstrip(',')
file.write(codes)
file.close()
print codes
print u'读取短线股串操作完成'

# 代码逻辑
# 1 从接口读取数据，并用正则过滤成数组，去重
# 2 读取本地blk文件，for写入
# 3 完成
# 4 读取dxg.blk的股票代码
# 5 输出成一行连续的代码串准备粘贴到自选股用
